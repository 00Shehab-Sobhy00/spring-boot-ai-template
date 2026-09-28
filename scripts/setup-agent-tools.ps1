# One-time, per-clone setup (Windows). Same as scripts/setup-agent-tools.sh, but with directory
# junctions: they need no admin rights or Developer Mode, unlike symlinks (ai/PROJECT_MEMORY.md →
# Environment Quirks). Safe to re-run.
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$target = (Resolve-Path 'ai\skills').Path

foreach ($link in '.claude\skills', '.agents\skills') {
    $item = Get-Item $link -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType) { Write-Output "ok      $link (already linked)"; continue }
    if ($item) { Write-Output "SKIP    $link exists and is not a link - move it away and re-run"; continue }
    New-Item -ItemType Directory -Force (Split-Path $link) | Out-Null
    New-Item -ItemType Junction -Path $link -Target $target | Out-Null
    Write-Output "linked  $link -> ai\skills"
}

if (Get-Command graphify -ErrorAction SilentlyContinue) {
    graphify install | Out-Null; Write-Output 'ok      graphify skill (user-level)'
    graphify hook install | Out-Null; Write-Output 'ok      graphify git hooks'
} else {
    Write-Output 'info    graphify not installed - optional, see docs/deployment/onboarding.md'
}
