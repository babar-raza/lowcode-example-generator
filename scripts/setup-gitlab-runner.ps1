#!/usr/bin/env pwsh
# setup-gitlab-runner.ps1
# Automatic GitLab Runner registration for this project.
#
# Steps:
#   1. Reads gl_pat from system/user/session environment
#   2. Resolves project ID via GitLab API
#   3. Creates runner auth token via GitLab API (no browser needed)
#   4. Detects Docker container or binary installation
#   5. Registers runner with Docker executor
#   6. Adds gl_pat as masked CI/CD variable
#   7. Verifies and prints links
#
# Usage:
#   .\scripts\setup-gitlab-runner.ps1
#   .\scripts\setup-gitlab-runner.ps1 -Force       # re-register if already exists
#   .\scripts\setup-gitlab-runner.ps1 -SkipCiVar   # skip adding gl_pat variable
#   .\scripts\setup-gitlab-runner.ps1 -DryRun      # preview without executing

param(
    [string]$RunnerDescription = "local-docker-lowcode",
    [string]$DefaultImage      = "python:3.13-slim",
    [switch]$Force,
    [switch]$SkipCiVar,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# --- Config ------------------------------------------------------------------
$GITLAB_URL   = "https://gitlab.recruitize.ai"
$PROJECT_PATH = "sialkot/cantt-smallize/lowcode-example-generator"

# Pre-initialize all variables
$Pat              = ""
$ProjectId        = 0
$RunnerToken      = ""
$skipRegistration = $false
$runnerContainer  = ""
$runnerBinary     = $false

# --- Helpers -----------------------------------------------------------------
function Write-Step([string]$msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok([string]$msg)   { Write-Host "  [OK]   $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Fail([string]$msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

function Invoke-GL([string]$Method = "GET", [string]$Path, [string]$JsonBody = "") {
    $headers = @{ "PRIVATE-TOKEN" = $Pat }
    $uri = "$GITLAB_URL/api/v4$Path"
    if ($Method -eq "GET" -or $JsonBody -eq "") {
        return Invoke-RestMethod -Uri $uri -Headers $headers -Method $Method
    }
    return Invoke-RestMethod -Uri $uri -Headers $headers -Method $Method `
        -Body $JsonBody -ContentType "application/json"
}

# --- Step 0: Read gl_pat -----------------------------------------------------
Write-Step "Step 0 - Reading gl_pat"
$Pat = [System.Environment]::GetEnvironmentVariable("gl_pat", "Machine")
if (-not $Pat) { $Pat = [System.Environment]::GetEnvironmentVariable("gl_pat", "User") }
if (-not $Pat) { $Pat = $env:gl_pat }
if (-not $Pat) {
    Write-Fail "gl_pat not found in Machine, User, or session environment."
    Write-Host "  Set it: [System.Environment]::SetEnvironmentVariable('gl_pat','YOUR_PAT','Machine')"
    exit 1
}
Write-Ok "gl_pat found (length=$($Pat.Length))"
if ($DryRun) { Write-Warn "DRY RUN - API calls and registrations will be skipped." }

# --- Step 1: Resolve project ID ----------------------------------------------
Write-Step "Step 1 - Resolving project ID"
$encodedPath = [Uri]::EscapeDataString($PROJECT_PATH)
try {
    $project   = Invoke-GL -Path "/projects/$encodedPath"
    $ProjectId = $project.id
    Write-Ok "Project: $($project.name_with_namespace) (id=$ProjectId)"
} catch {
    Write-Fail "API call failed: $_"
    Write-Host "  Check: network, SSL cert, and that gl_pat has 'api' scope."
    exit 1
}

# --- Step 2: Check for existing runner ---------------------------------------
Write-Step "Step 2 - Checking existing runners"
try {
    $allRunners = Invoke-GL -Path "/projects/$ProjectId/runners"
    $existing   = $allRunners | Where-Object { $_.description -eq $RunnerDescription } |
                  Select-Object -First 1
} catch {
    $existing = $null
}

if ($existing -and -not $Force) {
    Write-Warn "Runner '$RunnerDescription' already registered (id=$($existing.id)). Use -Force to re-register."
    $skipRegistration = $true
} else {
    if ($existing) { Write-Warn "Force: adding new registration alongside existing id=$($existing.id)" }
    Write-Ok "Proceeding with registration."
    $skipRegistration = $false
}

# --- Step 3: Create runner token via API -------------------------------------
if (-not $skipRegistration) {
    Write-Step "Step 3 - Creating runner token via GitLab API"
    if ($DryRun) {
        Write-Warn "DRY RUN: would POST /api/v4/user/runners"
    } else {
        $body = '{"runner_type":"project_type","project_id":' + $ProjectId +
                ',"description":"' + $RunnerDescription + '","run_untagged":true}'
        try {
            $result      = Invoke-GL -Method "POST" -Path "/user/runners" -JsonBody $body
            $RunnerToken = $result.token
            Write-Ok "Token: $($RunnerToken.Substring(0,[Math]::Min(12,$RunnerToken.Length)))..."
        } catch {
            Write-Fail "POST /user/runners failed: $_"
            Write-Host "  Requires GitLab >= 15.10."
            Write-Host "  Fallback: get token from $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd"
            exit 1
        }
    }
}

# --- Step 4: Detect runner installation --------------------------------------
Write-Step "Step 4 - Detecting gitlab-runner"
try {
    $containers = docker ps --format "{{.Names}}" 2>$null
    if ($containers) {
        $runnerContainer = ($containers |
            Where-Object { $_ -match "gitlab-runner" } |
            Select-Object -First 1)
        if ($null -eq $runnerContainer) { $runnerContainer = "" }
    }
} catch {
    $runnerContainer = ""
}

if (-not $runnerContainer) {
    if (Get-Command "gitlab-runner" -ErrorAction SilentlyContinue) {
        $runnerBinary = $true
    }
}

if ($runnerContainer) {
    Write-Ok "Docker container: $runnerContainer"
} elseif ($runnerBinary) {
    Write-Ok "gitlab-runner binary found in PATH"
} else {
    Write-Fail "gitlab-runner not found."
    Write-Host "  Start: docker run -d --name gitlab-runner --restart always -v /var/run/docker.sock:/var/run/docker.sock -v gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner:latest"
    exit 1
}

# --- Step 5: Register --------------------------------------------------------
Write-Step "Step 5 - Registering runner"
if ($skipRegistration) {
    Write-Warn "Skipped (already registered)."
} elseif ($DryRun) {
    Write-Warn "DRY RUN: would register --executor docker --docker-image $DefaultImage"
} elseif ($RunnerToken) {
    $regArgs = @(
        "register", "--non-interactive",
        "--url",          $GITLAB_URL,
        "--token",        $RunnerToken,
        "--executor",     "docker",
        "--docker-image", $DefaultImage,
        "--description",  $RunnerDescription
    )
    try {
        if ($runnerContainer) {
            docker exec $runnerContainer gitlab-runner @regArgs
        } else {
            & gitlab-runner @regArgs
        }
        Write-Ok "Registered successfully."
    } catch {
        Write-Fail "Registration failed: $_"
        exit 1
    }
}

# --- Step 6: Add gl_pat as CI/CD variable ------------------------------------
Write-Step "Step 6 - Upserting gl_pat CI/CD variable"
if ($SkipCiVar) {
    Write-Warn "Skipped (-SkipCiVar)."
} elseif ($DryRun) {
    Write-Warn "DRY RUN: would upsert gl_pat (masked + protected) via API."
} else {
    $updateBody = '{"value":"' + $Pat + '","masked":true,"protected":true}'
    $createBody = '{"key":"gl_pat","value":"' + $Pat +
                  '","variable_type":"env_var","masked":true,"protected":true}'
    try {
        $null = Invoke-GL -Method "PUT" -Path "/projects/$ProjectId/variables/gl_pat" `
                          -JsonBody $updateBody
        Write-Ok "gl_pat updated (masked + protected)."
    } catch {
        try {
            $null = Invoke-GL -Method "POST" -Path "/projects/$ProjectId/variables" `
                              -JsonBody $createBody
            Write-Ok "gl_pat created (masked + protected)."
        } catch {
            Write-Warn "Could not upsert gl_pat: $_ (needs Maintainer role)"
        }
    }
}

# --- Step 7: Verify ----------------------------------------------------------
Write-Step "Step 7 - Verifying runner"
if ($DryRun) {
    Write-Warn "DRY RUN: would run gitlab-runner verify"
} else {
    try {
        if ($runnerContainer) {
            docker exec $runnerContainer gitlab-runner verify 2>&1 |
                Select-String -Pattern "(Verifying|alive|ERROR)" |
                ForEach-Object { Write-Host "  $_" }
        } else {
            gitlab-runner verify 2>&1 |
                Select-String -Pattern "(Verifying|alive|ERROR)" |
                ForEach-Object { Write-Host "  $_" }
        }
    } catch {
        Write-Warn "Verify failed: $_ (runner may still work)"
    }
}

# --- Done --------------------------------------------------------------------
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host " Setup complete." -ForegroundColor Green
Write-Host ""
Write-Host " Runner settings : $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd"
Write-Host " Pipelines       : $GITLAB_URL/$PROJECT_PATH/-/pipelines"
Write-Host "=============================================" -ForegroundColor Green
