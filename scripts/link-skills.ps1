<#
.SYNOPSIS
    Link every skill under .agent/skills/ into .claude/skills/ so Claude Code
    can discover them as user-invocable skills.

.DESCRIPTION
    Creates Windows directory junctions (no admin rights required). Idempotent:
    re-running refreshes stale junctions without touching real content.

.PARAMETER ProjectRoot
    Root of the exam-lab project (the repo that contains .agent/skills/).
    Defaults to three levels up from this script.

.EXAMPLE
    .\link-skills.ps1
    .\link-skills.ps1 -ProjectRoot C:\path\to\ccnp-spri-labs
#>

param(
    [string]$ProjectRoot = $null
)

$ErrorActionPreference = "Stop"

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir  = (Resolve-Path (Join-Path $ScriptDir "..")).Path
if (-not $ProjectRoot) {
    $ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
}

if (-not (Test-Path (Join-Path $ProjectRoot ".agent\skills"))) {
    Write-Host "ERROR: $ProjectRoot\.agent\skills not found. Pass -ProjectRoot." -ForegroundColor Red
    exit 1
}

$ClaudeSkills = Join-Path $ProjectRoot ".claude\skills"
New-Item -ItemType Directory -Path $ClaudeSkills -Force | Out-Null

$linked = 0
$skipped = 0
Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
    $name = $_.Name
    $skillFile = Join-Path $_.FullName "SKILL.md"
    if (-not (Test-Path $skillFile)) { return }

    $link = Join-Path $ClaudeSkills $name
    $target = $_.FullName

    if (Test-Path $link) {
        $item = Get-Item $link -Force
        if ($item.LinkType -eq "Junction" -or $item.LinkType -eq "SymbolicLink") {
            # PS 5.1 has a known bug where Remove-Item on a junction throws
            # NullReferenceException despite removing it. Use .NET API instead.
            [System.IO.Directory]::Delete($link, $false)
        } else {
            Write-Host "  skip  $name  (exists as non-link directory)"
            $script:skipped++
            return
        }
    }

    New-Item -ItemType Junction -Path $link -Target $target | Out-Null
    Write-Host "  link  $name"
    $script:linked++
}

Write-Host ""
Write-Host "Linked $linked skill(s) into .claude\skills\; $skipped skipped."
Write-Host "Ensure .claude/skills/ is in your .gitignore (these are derived from the submodule)."
