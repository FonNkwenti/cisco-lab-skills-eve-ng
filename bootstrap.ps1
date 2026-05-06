<#
.SYNOPSIS
    Bootstrap a new Cisco certification lab project.

.DESCRIPTION
    Creates a new exam-specific lab repository with full structure, scaffolding,
    and submodule setup. Windows PowerShell version (no WSL required).

.PARAMETER ProjectName
    Name of the new project (e.g., "ccnp-encor-labs")

.PARAMETER CertName
    Full certification name (e.g., "CCNP ENCOR")

.PARAMETER ExamCode
    Exam code (e.g., "350-401")

.EXAMPLE
    .\bootstrap.ps1 -ProjectName "ccnp-encor-labs" -CertName "CCNP ENCOR" -ExamCode "350-401"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,

    [Parameter(Mandatory=$true)]
    [string]$CertName,

    [Parameter(Mandatory=$true)]
    [string]$ExamCode,

    [Parameter(Mandatory=$false)]
    [string]$ExamFullName = ""
)

$ErrorActionPreference = "Stop"

if (-not $ExamFullName) { $ExamFullName = $CertName }

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$HUB_DIR = $SCRIPT_DIR
$TARGET_DIR = Join-Path (Split-Path -Parent $HUB_DIR) $ProjectName
$GITHUB_HUB_URL = "https://github.com/FonNkwenti/cisco-lab-skills-eve-ng.git"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "  Bootstrapping: $ProjectName"
Write-Host "  Certification: $CertName ($ExamCode)"
Write-Host "  Target:        $TARGET_DIR"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if (Test-Path $TARGET_DIR) {
    Write-Host "ERROR: $TARGET_DIR already exists. Aborting." -ForegroundColor Red
    exit 1
}

try {
    Write-Host "→ Creating directory structure..."
    $dirs = @(
        ".agent",
        ".claude/commands",
        "blueprint/$ExamCode",
        "blueprint/$ExamCode/references",
        "specs",
        "conductor/tracks",
        "labs",
        "tests",
        "docs",
        ".prompts",
        "tasks"
    )

    foreach ($dir in $dirs) {
        $path = Join-Path $TARGET_DIR $dir
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }

    Write-Host "→ Initializing git repo..."
    & git init $TARGET_DIR

    Write-Host "→ Adding cisco-lab-skills as submodule at .agent/skills/ ..."
    & git -C $TARGET_DIR submodule add $GITHUB_HUB_URL .agent/skills

    Write-Host "→ Copying scaffolding..."
    Copy-Item (Join-Path $HUB_DIR "scaffolding/gitignore.template") (Join-Path $TARGET_DIR ".gitignore") -Force
    Copy-Item (Join-Path $HUB_DIR "scaffolding/requirements.txt") (Join-Path $TARGET_DIR "requirements.txt") -Force
    Copy-Item (Join-Path $HUB_DIR "scaffolding/labs-common") (Join-Path $TARGET_DIR "labs/common") -Recurse -Force

    Write-Host "-> Copying slash commands..."
    $cmdSrc = Join-Path $HUB_DIR "scaffolding/.claude/commands"
    $cmdDst = Join-Path $TARGET_DIR ".claude/commands"
    Copy-Item (Join-Path $cmdSrc "*") $cmdDst -Recurse -Force

    Write-Host "-> Installing telemetry hook (Stop hook -> .claude/last_run.json)..."
    $hookDst = Join-Path $TARGET_DIR ".claude/hooks"
    New-Item -ItemType Directory -Path $hookDst -Force | Out-Null
    Copy-Item (Join-Path $HUB_DIR "scaffolding/.claude/hooks/capture_telemetry.py") (Join-Path $hookDst "capture_telemetry.py") -Force
    Copy-Item (Join-Path $HUB_DIR "scaffolding/.claude/settings.json") (Join-Path $TARGET_DIR ".claude/settings.json") -Force

    Write-Host "-> Copying telemetry & cost documentation..."
    Copy-Item (Join-Path $HUB_DIR "scaffolding/docs/telemetry-and-cost.md") (Join-Path $TARGET_DIR "docs/telemetry-and-cost.md") -Force

    Write-Host "→ Generating conductor files..."
    Copy-Item (Join-Path $HUB_DIR "conductor-template/workflow.md") (Join-Path $TARGET_DIR "conductor/workflow.md") -Force
    Copy-Item (Join-Path $HUB_DIR "conductor-template/tech-stack.md") (Join-Path $TARGET_DIR "conductor/tech-stack.md") -Force
    Copy-Item (Join-Path $HUB_DIR "conductor-template/code_styleguides") (Join-Path $TARGET_DIR "conductor/code_styleguides") -Recurse -Force
    Copy-Item (Join-Path $HUB_DIR "conductor-template/tracks.md") (Join-Path $TARGET_DIR "conductor/tracks.md") -Force

    # Generate product.md from template
    $productTmpl = Get-Content (Join-Path $HUB_DIR "conductor-template/product.md.tmpl") -Raw
    $productContent = $productTmpl.Replace('{{CERT_NAME}}', $CertName).Replace('{{EXAM_CODE}}', $ExamCode).Replace('{{SCOPE}}', 'TODO: Define scope of coverage')
    Set-Content -Path (Join-Path $TARGET_DIR "conductor/product.md") -Value $productContent

    # Generate product-guidelines.md from template
    $guidelinesTmpl = Get-Content (Join-Path $HUB_DIR "conductor-template/product-guidelines.md.tmpl") -Raw
    $guidelinesContent = $guidelinesTmpl.Replace('{{CERT_NAME}}', $CertName).Replace('{{EXAM_CODE}}', $ExamCode)
    Set-Content -Path (Join-Path $TARGET_DIR "conductor/product-guidelines.md") -Value $guidelinesContent

    Write-Host "→ Generating tasks/ files..."
    $lessonsTmpl = Get-Content (Join-Path $HUB_DIR "scaffolding/tasks/lessons.md.tmpl") -Raw
    $lessonsContent = $lessonsTmpl.Replace('{{CERT_NAME}}', $CertName).Replace('{{EXAM_CODE}}', $ExamCode)
    Set-Content -Path (Join-Path $TARGET_DIR "tasks/lessons.md") -Value $lessonsContent

    $todoTmpl = Get-Content (Join-Path $HUB_DIR "scaffolding/tasks/todo.md.tmpl") -Raw
    $todoContent = $todoTmpl.Replace('{{CERT_NAME}}', $CertName).Replace('{{EXAM_CODE}}', $ExamCode)
    Set-Content -Path (Join-Path $TARGET_DIR "tasks/todo.md") -Value $todoContent

    Write-Host "→ Creating CLAUDE.md..."
    $fence = '```'
    $claudeMdPath = Join-Path $TARGET_DIR "CLAUDE.md"
    $claudeMdContent = @"
# $CertName ($ExamCode) Lab Project

## Shared Context (Skills + Standards)

See .agent/skills/memory/CLAUDE.md for the foundation skills repository context.

## This Certification

- **Exam**: $CertName ($ExamCode)
- **Audience**: Network engineers preparing for the $ExamCode exam
- **Platform**: EVE-NG on Dell Latitude 5540 (Intel/Windows)

## Project Structure

See conductor/product.md and conductor/workflow.md for detailed documentation.

## Active Work

- See conductor/tracks.md for the current chapter plan
- See labs/ for existing lab content
- Run git submodule status to check skills version

## Three-Phase Workflow (slash commands)

1. Phase 1 - Plan: Upload blueprint to blueprint/$ExamCode/blueprint.md, then run /plan-exam
2. Phase 2 - Spec: Run /create-spec <topic> per topic (review after each)
3. Phase 3 - Build: Run /build-lab <topic>/<lab-id> one lab at a time (review after each)

Additional commands: /build-capstone, /tag-lab, /sync-skills, /project-status. All commands live in .claude/commands/ - they warn on missing prerequisites but let you proceed (advisory gating).

## Common Commands

${fence}bash
# Update skills to latest
git submodule update --remote .agent/skills
git add .agent/skills

# Run lab setup
python labs/<topic>/lab-NN-<slug>/setup_lab.py --host <eve-ng-ip>

# Run tests
pytest tests/ -v
${fence}
"@
    Set-Content -Path $claudeMdPath -Value $claudeMdContent

    Write-Host "→ Generating README.md from template..."
    $readmeTmpl = Get-Content (Join-Path $HUB_DIR "scaffolding/README_template.md") -Raw
    $readmeContent = $readmeTmpl.
        Replace('{{EXAM_SHORT}}', $CertName).
        Replace('{{EXAM_CODE}}', $ExamCode).
        Replace('{{EXAM_NAME}}', $ExamFullName).
        Replace('{{PLATFORM}}', 'EVE-NG (Intel/Windows)').
        Replace('{{REPO_NAME}}', $ProjectName).
        Replace('{{TOPIC_COUNT}}', '_TBD — run /plan-exam_').
        Replace('{{TOTAL_LABS}}', '_TBD — run /plan-exam_').
        Replace('{{REFERENCE_LAB}}', '_TBD — first lab built in Phase 3_')
    Set-Content -Path (Join-Path $TARGET_DIR "README.md") -Value $readmeContent

    Write-Host "→ Generating STATUS.md from template..."
    $today = Get-Date -Format 'yyyy-MM-dd'
    $statusTmpl = Get-Content (Join-Path $HUB_DIR "scaffolding/STATUS_template.md") -Raw
    $statusContent = $statusTmpl.
        Replace('{{EXAM_SHORT}}', $CertName).
        Replace('{{EXAM_CODE}}', $ExamCode).
        Replace('{{LAST_UPDATED}}', $today).
        Replace('{{SKILLS_COMMIT}}', '(run /sync-skills)').
        Replace('{{SKILLS_BRANCH}}', 'main').
        Replace('{{BLUEPRINT_OBJECTIVES}}', '_pending blueprint upload_').
        Replace('{{PHASE_1_STATE}}', '— not started').
        Replace('{{PHASE_2_STATE}}', '— not started').
        Replace('{{PHASE_3_STATE}}', '— not started').
        Replace('{{TOPIC_ROWS}}', '| _run /plan-exam to populate_ |  |  |  |').
        Replace('{{RECENT_ACTIVITY}}', "_Project bootstrapped on $today. No activity yet._").
        Replace('{{NEXT_COMMAND}}', "Upload your exam blueprint to ``blueprint/$ExamCode/blueprint.md``, then run ``/plan-exam``.")
    Set-Content -Path (Join-Path $TARGET_DIR "STATUS.md") -Value $statusContent

    Write-Host "→ Linking skills into .claude\skills\ for Claude Code discovery..."
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $TARGET_DIR ".agent\skills\scripts\link-skills.ps1") -ProjectRoot $TARGET_DIR

    Write-Host "→ Initial commit..."
    & git -C $TARGET_DIR add -A
    & git -C $TARGET_DIR commit -m "chore: bootstrap $ProjectName from cisco-lab-skills template"

    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "  ✅ Done! Project: $TARGET_DIR"
    Write-Host ""
    Write-Host "  Next steps:"
    Write-Host "  1. Create GitHub repo and push: git remote add origin `<url`> `&`& git push"
    Write-Host "  2. Upload blueprint to blueprint/$ExamCode/blueprint.md, then run /plan-exam"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""
}
catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
