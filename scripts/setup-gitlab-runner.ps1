#!/usr/bin/env pwsh
# setup-gitlab-runner.ps1
# Fully automatic GitLab Runner registration for this project.
#
# What it does:
#   1. Reads gl_pat from the system environment
#   2. Resolves the GitLab project ID via API
#   3. Creates a runner authentication token via the GitLab API (no UI needed)
#   4. Detects whether gitlab-runner is a Docker container or a system binary
#   5. Registers the runner against this project
#   6. Adds gl_pat as a masked CI/CD variable in the project (for scheduled jobs)
#   7. Verifies and prints the pipeline URL
#
# Prerequisites:
#   - gl_pat set as a Windows system environment variable (write_repository + api scopes)
#   - Docker Desktop running (or gitlab-runner.exe in PATH)
#   - gitlab/gitlab-runner Docker container OR gitlab-runner.exe installed
#
# Usage (from repo root):
#   .\scripts\setup-gitlab-runner.ps1
#   .\scripts\setup-gitlab-runner.ps1 -Force          # re-register if already exists
#   .\scripts\setup-gitlab-runner.ps1 -SkipCiVar      # skip adding gl_pat CI variable
#   .\scripts\setup-gitlab-runner.ps1 -DryRun         # print steps without executing

param(
    [string]$RunnerDescription = "local-docker-lowcode",
    [string]$DefaultImage = "python:3.13-slim",
    [switch]$Force,
    [switch]$SkipCiVar,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Config ────────────────────────────────────────────────────────────────────
$GITLAB_URL  = "https://gitlab.recruitize.ai"
$PROJECT_PATH = "sialkot/cantt-smallize/lowcode-example-generator"

# ── Helpers ───────────────────────────────────────────────────────────────────
function Write-Step([string]$msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok([string]$msg)   { Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "  WARN $msg" -ForegroundColor Yellow }
function Write-Fail([string]$msg) { Write-Host "  FAIL $msg" -ForegroundColor Red }

function Invoke-GL {
    param([string]$Method = "GET", [string]$Path, [hashtable]$Body = @{})
    $uri = "$GITLAB_URL/api/v4$Path"
    $headers = @{ "PRIVATE-TOKEN" = $Pat }
    $params = @{ Uri = $uri; Headers = $headers; Method = $Method; ErrorAction = "Stop" }
    if ($Method -ne "GET" -and $Body.Count -gt 0) {
        $params["Body"] = ($Body | ConvertTo-Json -Depth 5)
        $params["ContentType"] = "application/json"
    }
    return Invoke-RestMethod @params
}

# ── Step 0: Read gl_pat ───────────────────────────────────────────────────────
Write-Step "Reading gl_pat"
$Pat = [System.Environment]::GetEnvironmentVariable("gl_pat", "Machine")
if (-not $Pat) { $Pat = $env:gl_pat }
if (-not $Pat) {
    Write-Fail "gl_pat not found in system or user environment variables."
    Write-Host "  Set it with: [System.Environment]::SetEnvironmentVariable('gl_pat','<value>','Machine')"
    exit 1
}
Write-Ok "gl_pat found (length=$($Pat.Length))"

if ($DryRun) { Write-Warn "DRY RUN mode — API calls and registrations will be skipped." }

# ── Step 1: Resolve project ID ────────────────────────────────────────────────
Write-Step "Resolving project ID"
$encodedPath = [System.Uri]::EscapeDataString($PROJECT_PATH)
$project = Invoke-GL -Path "/projects/$encodedPath"
$ProjectId = $project.id
Write-Ok "Project: $($project.name_with_namespace) (id=$ProjectId)"

# ── Step 2: Check for existing runner with same description ───────────────────
Write-Step "Checking for existing runners"
$existingRunners = Invoke-GL -Path "/projects/$ProjectId/runners"
$existing = $existingRunners | Where-Object { $_.description -eq $RunnerDescription }

if ($existing -and -not $Force) {
    Write-Warn "Runner '$RunnerDescription' already registered (id=$($existing.id)). Use -Force to re-register."
    Write-Ok "Skipping registration."
    $skipRegistration = $true
} else {
    if ($existing -and $Force) {
        Write-Warn "Force mode: will create new registration alongside existing runner id=$($existing.id)"
    } else {
        Write-Ok "No existing runner named '$RunnerDescription' — proceeding."
    }
    $skipRegistration = $false
}

# ── Step 3: Create runner auth token via API ──────────────────────────────────
$RunnerToken = $null
if (-not $skipRegistration) {
    Write-Step "Creating runner authentication token via GitLab API"
    if ($DryRun) {
        Write-Warn "DRY RUN: would POST /api/v4/user/runners"
    } else {
        try {
            $body = @{
                runner_type = "project_type"
                project_id  = $ProjectId
                description = $RunnerDescription
                run_untagged = $true
            }
            $result = Invoke-GL -Method "POST" -Path "/user/runners" -Body $body
            $RunnerToken = $result.token
            Write-Ok "Runner token obtained: $($RunnerToken.Substring(0,[Math]::Min(12,$RunnerToken.Length)))..."
        } catch {
            Write-Fail "GitLab API /user/runners failed: $_"
            Write-Host ""
            Write-Host "  Fallback: get a token manually from:" -ForegroundColor Yellow
            Write-Host "  $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd" -ForegroundColor Yellow
            Write-Host "  Then re-run: .\scripts\setup-gitlab-runner.ps1 -RunnerToken <token>" -ForegroundColor Yellow
            exit 1
        }
    }
}

# ── Step 4: Detect runner installation ────────────────────────────────────────
Write-Step "Detecting gitlab-runner installation"
$runnerContainer = $null
$runnerBinary    = $false

# Docker container?
try {
    $containers = docker ps --format "{{.Names}}" 2>$null
    $runnerContainer = $containers | Where-Object { $_ -match "gitlab-runner" } | Select-Object -First 1
} catch {}

# Binary in PATH?
if (-not $runnerContainer) {
    if (Get-Command "gitlab-runner" -ErrorAction SilentlyContinue) {
        $runnerBinary = $true
    } elseif (Get-Command "gitlab-runner.exe" -ErrorAction SilentlyContinue) {
        $runnerBinary = $true
    }
}

if ($runnerContainer) {
    Write-Ok "Using Docker container: $runnerContainer"
} elseif ($runnerBinary) {
    Write-Ok "Using gitlab-runner binary in PATH"
} else {
    Write-Fail "gitlab-runner not found."
    Write-Host "  Start it with: docker run -d --name gitlab-runner --restart always -v /var/run/docker.sock:/var/run/docker.sock -v gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner:latest"
    exit 1
}

# ── Step 5: Register ──────────────────────────────────────────────────────────
if (-not $skipRegistration -and -not $DryRun -and $RunnerToken) {
    Write-Step "Registering runner"

    $registerArgs = @(
        "register",
        "--non-interactive",
        "--url", $GITLAB_URL,
        "--token", $RunnerToken,
        "--executor", "docker",
        "--docker-image", $DefaultImage,
        "--description", $RunnerDescription
    )

    if ($runnerContainer) {
        docker exec $runnerContainer gitlab-runner @registerArgs
    } else {
        & gitlab-runner @registerArgs
    }
    Write-Ok "Runner registered."
} elseif ($DryRun) {
    Write-Warn "DRY RUN: would run gitlab-runner register --url $GITLAB_URL --executor docker --docker-image $DefaultImage"
}

# ── Step 6: Add gl_pat as CI/CD variable ──────────────────────────────────────
if (-not $SkipCiVar) {
    Write-Step "Adding gl_pat as GitLab CI/CD variable"
    if ($DryRun) {
        Write-Warn "DRY RUN: would POST /api/v4/projects/$ProjectId/variables key=gl_pat masked=true protected=true"
    } else {
        # Check if variable already exists
        try {
            $existingVar = Invoke-GL -Path "/projects/$ProjectId/variables/gl_pat" -ErrorAction SilentlyContinue
            Write-Warn "Variable gl_pat already exists — updating value."
            $null = Invoke-GL -Method "PUT" -Path "/projects/$ProjectId/variables/gl_pat" -Body @{
                value     = $Pat
                masked    = $true
                protected = $true
            }
            Write-Ok "gl_pat variable updated."
        } catch {
            # Variable doesn't exist yet — create it
            $null = Invoke-GL -Method "POST" -Path "/projects/$ProjectId/variables" -Body @{
                key       = "gl_pat"
                value     = $Pat
                variable_type = "env_var"
                masked    = $true
                protected = $true
            }
            Write-Ok "gl_pat variable created (masked + protected)."
        }
    }
}

# ── Step 7: Verify ────────────────────────────────────────────────────────────
Write-Step "Verifying runner"
if (-not $DryRun) {
    if ($runnerContainer) {
        docker exec $runnerContainer gitlab-runner verify 2>&1 | Select-String -Pattern "(Verifying|alive|error)"
    } else {
        gitlab-runner verify 2>&1 | Select-String -Pattern "(Verifying|alive|error)"
    }
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host " Setup complete." -ForegroundColor Green
Write-Host ""
Write-Host " Runner settings : $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd"
Write-Host " Pipelines       : $GITLAB_URL/$PROJECT_PATH/-/pipelines"
Write-Host " Trigger pipeline: git push origin main"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
