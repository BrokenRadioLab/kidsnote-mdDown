"""Export Kidsnote reports as Obsidian-friendly Markdown files.

This module keeps the Kidsnote fetching layer independent from any hosted
destination. It writes one Markdown note per report, stores attachments next to
the vault, and optionally uses a local Ollama model for short summaries,
monthly growth stories, and milestone extraction.
"""
from __future__ import annotations

import io
import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

_LOGGER = logging.getLogger(__name__)

IMAGE_URL_KEYS = ("original", "url", "src", "high", "high_resize", "large_resize")
MAX_IMAGE_SIDE = 1920

WEATHER_DISPLAY = {
    "sunny": ("☀️", "맑음"),
    "partly_cloudy": ("⛅", "구름 조금"),
    "mostly_cloudy": ("🌥️", "구름 많음"),
    "overcast": ("☁️", "흐림"),
    "cloudy": ("☁️", "흐림"),
    "fog": ("🌫️", "안개"),
    "foggy": ("🌫️", "안개"),
    "rain": ("🌧️", "비"),
    "rainy": ("🌧️", "비"),
    "sunny_after_rain": ("🌦️", "비 온 뒤 맑음"),
    "snow": ("❄️", "눈"),
    "snowy": ("❄️", "눈"),
    "yellow_sand": ("😷", "황사"),
    "thunderstorm": ("⛈️", "천둥번개"),
    "stormy": ("⛈️", "폭풍"),
    "mixed_rain_snow": ("🌨️", "진눈깨비"),
    "windy": ("🌬️", "바람"),
    "hot": ("🔥", "더움"),
    "cold": ("🧊", "추움"),
}

AUTHOR_FILE_LABELS = {
    "teacher": "교사알림장",
    "parent": "부모알림장",
    "admin": "공지알림장",
}


def _safe_filename(value: str, fallback: str = "note") -> str:
    value = re.sub(r"[\\/:*?\"<>|#^\[\]]+", " ", value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value[:80].strip() or fallback


def _frontmatter_string(value: Any) -> str:
    text = str(value or "")
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _date_from_report(report: dict[str, Any]) -> str:
    raw = (
        report.get("date_written")
        or (report.get("modified") or "")[:10]
        or (report.get("created") or "")[:10]
    )
    if raw:
        return str(raw)[:10]
    return datetime.now().date().isoformat()


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for idx in range(2, 1000):
        candidate = path.with_name(f"{stem} ({idx}){suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a unique filename for {path}")


def _read_report_id(path: Path) -> int | None:
    return _read_frontmatter_id(path, "report_id")


def _read_frontmatter_id(path: Path, key: str) -> int | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:1200]
    except Exception:
        return None
    match = re.search(rf"^{re.escape(key)}:\s*(\d+)\s*$", text, re.MULTILINE)
    if not match:
        return None
    return int(match.group(1))


def _first_attachment_url(obj: dict[str, Any]) -> str:
    for key in IMAGE_URL_KEYS:
        url = obj.get(key)
        if url:
            return str(url)
    return ""


def _weather_text(code: str) -> str:
    if not code:
        return ""
    emoji, label = WEATHER_DISPLAY.get(code, ("🌤️", code))
    return f"{emoji} 날씨: {label}"


def _author_file_label(report: dict[str, Any]) -> str:
    author_type = (report.get("author") or {}).get("type") or ""
    return AUTHOR_FILE_LABELS.get(author_type, "알림장")


def _strip_gps(raw: bytes) -> bytes:
    try:
        import piexif  # type: ignore[import-not-found]
    except Exception:
        return raw
    try:
        exif = piexif.load(raw)
    except Exception:
        return raw
    changed = False
    if exif.get("GPS"):
        exif["GPS"] = {}
        changed = True
    exif_ifd = exif.get("Exif") or {}
    if piexif.ExifIFD.MakerNote in exif_ifd:
        exif_ifd.pop(piexif.ExifIFD.MakerNote, None)
        exif["Exif"] = exif_ifd
        changed = True
    if not changed:
        return raw
    try:
        out = io.BytesIO()
        piexif.insert(piexif.dump(exif), raw, out)
        return out.getvalue()
    except Exception:
        return raw


def _normalize_image(raw: bytes, filename: str) -> tuple[bytes, str]:
    """Strip GPS metadata and downsize very large images for vault comfort."""
    suffix = Path(filename).suffix.lower()
    if suffix not in (".jpg", ".jpeg"):
        return raw, filename
    raw = _strip_gps(raw)
    try:
        from PIL import Image, ImageOps  # type: ignore[import-not-found]
    except Exception:
        return raw, filename
    try:
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img)
        if max(img.size) <= MAX_IMAGE_SIDE:
            return raw, filename
        ratio = MAX_IMAGE_SIDE / max(img.size)
        size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(size, Image.LANCZOS)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=85, optimize=True, progressive=True)
        return out.getvalue(), Path(filename).with_suffix(".jpg").name
    except Exception:
        return raw, filename


class MarkdownExporter:
    """Write Kidsnote data into an Obsidian vault layout."""

    def __init__(self, root: Path, *, enable_llm: bool = True) -> None:
        self.root = root
        self.kidsnote_dir = root
        self.enable_llm = enable_llm
        self._ollama_checked = False
        self._ollama: dict[str, str] | None = None

    def ensure_dirs(self) -> None:
        self.kidsnote_dir.mkdir(parents=True, exist_ok=True)

    def _child_name(self, report: dict[str, Any], fallback: str = "Unknown") -> str:
        raw = report.get("child_name") or fallback
        return _safe_filename(str(raw), fallback)

    def _child_root(self, child_name: str) -> Path:
        return self.kidsnote_dir / _safe_filename(child_name, "Unknown")

    def _dashboards_dir(self, child_name: str) -> Path:
        return self._child_root(child_name) / "_index"

    def _notice_root(self, child_name: str) -> Path:
        return self._child_root(child_name) / "공지사항"

    def existing_report_ids(self) -> set[int]:
        self.ensure_dirs()
        out: set[int] = set()
        for path in self.kidsnote_dir.rglob("*.md"):
            report_id = _read_report_id(path)
            if report_id is not None:
                out.add(report_id)
        return out

    def _existing_note_paths(self, child_name: str, report_id: int) -> list[Path]:
        child_root = self._child_root(child_name)
        if not child_root.exists():
            return []
        return [
            path for path in child_root.rglob("*.md")
            if _read_report_id(path) == report_id
        ]

    def _existing_notice_paths(self, child_name: str, notice_id: int) -> list[Path]:
        notice_root = self._notice_root(child_name)
        if not notice_root.exists():
            return []
        return [
            path for path in notice_root.rglob("*.md")
            if _read_frontmatter_id(path, "notice_id") == notice_id
        ]

    def export_report(
        self,
        report: dict[str, Any],
        kidsnote_sess: requests.Session,
        *,
        attached_menu: dict[str, Any] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        self.ensure_dirs()
        report_id = int(report["id"])
        date = _date_from_report(report)
        child_name = self._child_name(report)
        ym_dir = self._child_root(child_name) / date[:4] / date[5:7]
        ym_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{date}_{_author_file_label(report)}.md"
        note_path = ym_dir / filename

        existing_note_paths = self._existing_note_paths(child_name, report_id)
        if existing_note_paths and not force:
            return {
                "path": str(existing_note_paths[0]),
                "images": 0,
                "files": 0,
                "skipped": True,
            }

        if note_path.exists() and note_path not in existing_note_paths:
            note_path = _unique_path(note_path)

        asset_dir = ym_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)

        image_links = self._download_images(report, kidsnote_sess, asset_dir)
        file_links = self._download_blobs(report, kidsnote_sess, asset_dir)
        summary = self.summarize_report(report) if self.enable_llm else ""

        note_path.write_text(
            self._render_report_markdown(
                report, note_path, image_links, file_links, summary,
                attached_menu=attached_menu,
            ),
            encoding="utf-8",
        )
        for old_path in existing_note_paths:
            if old_path != note_path and old_path.exists():
                old_path.unlink()
        _LOGGER.info("Markdown +1 id=%s -> %s", report_id, note_path)
        return {
            "path": str(note_path),
            "images": len(image_links),
            "files": len(file_links),
            "skipped": False,
        }

    def export_notice(
        self,
        notice: dict[str, Any],
        kidsnote_sess: requests.Session,
        *,
        child_name: str,
        force: bool = False,
    ) -> dict[str, Any]:
        self.ensure_dirs()
        notice_id = int(notice["id"])
        date = _date_from_report(notice)
        ym_dir = self._notice_root(child_name) / date[:4] / date[5:7]
        ym_dir.mkdir(parents=True, exist_ok=True)

        title = _safe_filename((notice.get("title") or "공지사항").strip(), "공지사항")
        note_path = ym_dir / f"{date}_{title}.md"

        existing_note_paths = self._existing_notice_paths(child_name, notice_id)
        if existing_note_paths and not force:
            return {
                "path": str(existing_note_paths[0]),
                "images": 0,
                "files": 0,
                "skipped": True,
            }

        if note_path.exists() and note_path not in existing_note_paths:
            note_path = _unique_path(note_path)

        asset_dir = ym_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)
        image_links = self._download_images(notice, kidsnote_sess, asset_dir)
        file_links = self._download_blobs(notice, kidsnote_sess, asset_dir)

        note_path.write_text(
            self._render_notice_markdown(notice, image_links, file_links),
            encoding="utf-8",
        )
        for old_path in existing_note_paths:
            if old_path != note_path and old_path.exists():
                old_path.unlink()
        _LOGGER.info("Markdown notice +1 id=%s -> %s", notice_id, note_path)
        return {
            "path": str(note_path),
            "images": len(image_links),
            "files": len(file_links),
            "skipped": False,
        }

    def _download_images(
        self,
        report: dict[str, Any],
        sess: requests.Session,
        asset_dir: Path,
    ) -> list[Path]:
        out: list[Path] = []
        report_id = int(report.get("id", 0))
        date_compact = _date_from_report(report).replace("-", "")
        for idx, img in enumerate(report.get("attached_images") or [], start=1):
            if not isinstance(img, dict):
                continue
            url = _first_attachment_url(img)
            if not url:
                continue
            hint = img.get("original_file_name") or Path(urlparse(url).path).name
            suffix = Path(str(hint)).suffix or ".jpg"
            filename = f"{date_compact}_{report_id}_{idx:03d}{suffix.lower()}"
            path = asset_dir / filename
            if path.exists():
                out.append(path)
                continue
            try:
                resp = sess.get(url, timeout=180)
                resp.raise_for_status()
                data, normalized_name = _normalize_image(resp.content, filename)
                path = asset_dir / normalized_name
                path.write_bytes(data)
                out.append(path)
            except Exception as exc:
                _LOGGER.warning("image download failed for report %s: %s", report.get("id"), exc)
        return out

    def _download_blobs(
        self,
        report: dict[str, Any],
        sess: requests.Session,
        asset_dir: Path,
    ) -> list[Path]:
        out: list[Path] = []
        report_id = int(report.get("id", 0))
        date_compact = _date_from_report(report).replace("-", "")
        objects: list[tuple[str, dict[str, Any]]] = []
        video = report.get("attached_video") or report.get("video")
        if isinstance(video, dict):
            objects.append(("video", video))
        elif isinstance(video, list):
            objects.extend(("video", x) for x in video if isinstance(x, dict))
        objects.extend(("file", x) for x in (report.get("attached_files") or []) if isinstance(x, dict))

        for idx, (kind, obj) in enumerate(objects, start=1):
            url = obj.get("original") or obj.get("url")
            if not url:
                continue
            hint = obj.get("original_file_name") or Path(urlparse(str(url)).path).name
            suffix = Path(str(hint)).suffix or (".mp4" if kind == "video" else ".bin")
            stem = _safe_filename(Path(str(hint)).stem, kind)
            path = asset_dir / f"{date_compact}_{report_id}_{kind}_{idx:03d}_{stem}{suffix.lower()}"
            if path.exists():
                out.append(path)
                continue
            try:
                resp = sess.get(url, timeout=240)
                resp.raise_for_status()
                path.write_bytes(resp.content)
                out.append(path)
            except Exception as exc:
                _LOGGER.warning("%s download failed for report %s: %s", kind, report.get("id"), exc)
        return out

    def _render_report_markdown(
        self,
        report: dict[str, Any],
        note_path: Path,
        image_links: list[Path],
        file_links: list[Path],
        summary: str,
        *,
        attached_menu: dict[str, Any] | None,
    ) -> str:
        report_id = int(report["id"])
        date = _date_from_report(report)
        author = (report.get("author") or {}).get("type") or ""
        child_name = report.get("child_name") or ""
        weather = report.get("weather") or ""
        body = (report.get("content") or "").strip()

        lines = [
            "---",
            "type: kidsnote-report",
            f"report_id: {report_id}",
            f'date: "{_frontmatter_string(date)}"',
            f'author: "{_frontmatter_string(author)}"',
            f'child: "{_frontmatter_string(child_name)}"',
            f'weather: "{_frontmatter_string(weather)}"',
            "tags:",
            "  - kidsnote",
            "  - alimnota",
            "---",
            "",
        ]
        weather_text = _weather_text(weather)
        if weather_text:
            lines.extend([f"> {weather_text}", ""])
        if summary:
            lines.extend(["## Summary", "", summary.strip(), ""])
        lines.extend(["## Original", "", body or "(empty)", ""])

        if image_links:
            lines.extend(["## Photos", ""])
            for path in image_links:
                lines.append(f"![{path.name}](assets/{path.name})")
            lines.append("")

        if file_links:
            lines.extend(["## Attachments", ""])
            for path in file_links:
                lines.append(f"- [{path.name}](assets/{path.name})")
            lines.append("")

        if attached_menu:
            menu_text = self._menu_text(attached_menu)
            if menu_text:
                lines.extend(["## Menu", "", menu_text, ""])

        return "\n".join(lines).rstrip() + "\n"

    def _render_notice_markdown(
        self,
        notice: dict[str, Any],
        image_links: list[Path],
        file_links: list[Path],
    ) -> str:
        notice_id = int(notice["id"])
        date = _date_from_report(notice)
        title = (notice.get("title") or "공지사항").strip()
        body = (notice.get("content") or "").strip()
        author_name = notice.get("author_name") or ""
        lines = [
            "---",
            "type: kidsnote-notice",
            f"notice_id: {notice_id}",
            f'date: "{_frontmatter_string(date)}"',
            f'title: "{_frontmatter_string(title)}"',
            f'author: "{_frontmatter_string(author_name)}"',
            "tags:",
            "  - kidsnote",
            "  - notice",
            "---",
            "",
        ]
        meta_bits = []
        if author_name:
            meta_bits.append(f"작성: {author_name}")
        if notice.get("is_center_notice"):
            meta_bits.append("센터 공지")
        if notice.get("is_always_on_top"):
            meta_bits.append("상단 고정")
        if meta_bits:
            lines.extend(["> " + " · ".join(meta_bits), ""])
        lines.extend(["## Notice", "", body or "(empty)", ""])

        if image_links:
            lines.extend(["## Photos", ""])
            for path in image_links:
                lines.append(f"![{path.name}](assets/{path.name})")
            lines.append("")

        if file_links:
            lines.extend(["## Attachments", ""])
            for path in file_links:
                lines.append(f"- [{path.name}](assets/{path.name})")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _menu_text(self, menu: dict[str, Any]) -> str:
        labels = {
            "morning": "Morning",
            "morning_snack": "Morning snack",
            "lunch": "Lunch",
            "afternoon_snack": "Afternoon snack",
            "dinner": "Dinner",
        }
        rows = []
        for key, label in labels.items():
            value = (menu.get(key) or "").strip()
            if value:
                rows.append(f"- **{label}**: {value}")
        return "\n".join(rows)

    def publish_growth_stories(self, reports: list[dict[str, Any]], child_name: str = "") -> Path | None:
        if not self.enable_llm or self._ollama_config() is None:
            return None
        self.ensure_dirs()
        child_name = child_name or self._child_name(reports[0]) if reports else "Unknown"
        dashboards_dir = self._dashboards_dir(child_name)
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for report in reports:
            date = _date_from_report(report)
            by_month[date[:7]].append(report)
        lines = [
            "---",
            "type: kidsnote-dashboard",
            "dashboard: monthly-growth-stories",
            "tags:",
            "  - kidsnote",
            "  - growth",
            "---",
            "",
            "# Monthly Growth Stories",
            "",
        ]
        for ym in sorted(by_month):
            joined = "\n\n".join((r.get("content") or "").strip()[:250] for r in by_month[ym])[:3500]
            if len(joined.strip()) < 80:
                continue
            prompt = (
                "다음은 한 달치 키즈노트 알림장입니다. 실제 기록에 근거해서 "
                "아이의 성장과 변화가 드러나는 한국어 요약을 3-5문장으로 작성하세요. "
                "없는 내용은 만들지 마세요.\n\n"
                f"[{ym} 기록]\n{joined}\n\n요약:"
            )
            story = self._ask_ollama(prompt, max_chars=900, timeout=600)
            if story:
                lines.extend([f"## {ym}", "", story.strip(), ""])
        path = dashboards_dir / "monthly-growth-stories.md"
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return path

    def publish_milestones(self, reports: list[dict[str, Any]], child_name: str = "") -> Path | None:
        if not self.enable_llm or self._ollama_config() is None:
            return None
        self.ensure_dirs()
        child_name = child_name or self._child_name(reports[0]) if reports else "Unknown"
        dashboards_dir = self._dashboards_dir(child_name)
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        lines = [
            "---",
            "type: kidsnote-dashboard",
            "dashboard: milestones",
            "tags:",
            "  - kidsnote",
            "  - milestones",
            "---",
            "",
            "# Milestones",
            "",
        ]
        seen: set[str] = set()
        for report in sorted(reports, key=_date_from_report):
            body = (report.get("content") or "").strip()
            if len(body) < 40:
                continue
            date = _date_from_report(report)
            prompt = (
                "다음 키즈노트 알림장에서 아이의 발달/성장 마일스톤이 뚜렷하면 "
                "20자 이내의 짧은 명사구 하나만 답하세요. 없으면 '없음'만 답하세요. "
                "예: 친구에게 양보, 노래 리듬 표현, 첫 가위질\n\n"
                f"알림장:\n{body[:1200]}\n\n마일스톤:"
            )
            milestone = self._ask_ollama(prompt, max_chars=80, timeout=90)
            if not milestone:
                continue
            milestone = milestone.splitlines()[0].strip(" -`\"'")
            if "없음" in milestone or len(milestone) > 40:
                continue
            key = milestone.lower()
            if key in seen:
                continue
            seen.add(key)
            report_id = int(report.get("id", 0))
            lines.append(f"- **{date}**: {milestone} ^kidsnote-{report_id}")
        path = dashboards_dir / "milestones.md"
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return path

    def summarize_report(self, report: dict[str, Any]) -> str:
        body = (report.get("content") or "").strip()
        if len(body) < 40 or self._ollama_config() is None:
            return ""
        prompt = (
            "다음 키즈노트 알림장을 부모가 빠르게 볼 수 있도록 한국어로 2문장 이내로 요약하세요. "
            "실제 내용에 없는 사실은 추가하지 마세요.\n\n"
            f"알림장:\n{body[:1600]}\n\n요약:"
        )
        return self._ask_ollama(prompt, max_chars=450, timeout=120)

    def _ollama_config(self) -> dict[str, str] | None:
        if self._ollama_checked:
            return self._ollama
        self._ollama_checked = True
        host = os.environ.get("OLLAMA_HOST")
        if not host:
            return None
        model = os.environ.get("OLLAMA_MODEL") or "llama3.1:8b"
        try:
            resp = requests.get(f"{host.rstrip('/')}/api/version", timeout=5)
            resp.raise_for_status()
        except Exception as exc:
            _LOGGER.warning("OLLAMA_HOST is set but unavailable; LLM markdown sections skipped: %s", exc)
            return None
        self._ollama = {"host": host.rstrip("/"), "model": model}
        return self._ollama

    def _ask_ollama(self, prompt: str, *, max_chars: int, timeout: int) -> str:
        cfg = self._ollama_config()
        if cfg is None:
            return ""
        try:
            resp = requests.post(
                f"{cfg['host']}/api/generate",
                json={
                    "model": cfg["model"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 300},
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            text = (resp.json().get("response") or "").strip()
            return text[:max_chars].strip()
        except Exception as exc:
            _LOGGER.warning("Ollama request failed: %s", exc)
            return ""
