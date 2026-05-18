param(
    [string]$VaultPath = "D:\Obisian\Obsidian_Vault\KidsNote Backup",
    [switch]$NoLlm,
    [int]$Limit = 0,
    [switch]$MonthlySample,
    [switch]$ForceRefresh
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fetchScript = Join-Path $PSScriptRoot "fetch.py"

$argsList = @(
    "--auth-mode", "session-cookie-env",
    "--export-markdown",
    "--all-children",
    "--no-local-save",
    "--backup-root", $VaultPath
)

if ($NoLlm) {
    $argsList += "--no-llm"
}
if ($Limit -gt 0) {
    $argsList += @("--limit", "$Limit")
}
if ($MonthlySample) {
    $argsList += "--monthly-sample"
}
if ($ForceRefresh) {
    $argsList += "--force-refresh"
}

Push-Location $repoRoot
try {
    python $fetchScript @argsList
}
finally {
    Pop-Location
}

