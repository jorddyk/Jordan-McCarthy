[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$EulerUser,

    [ValidateSet('Submit', 'Status')]
    [string]$Action = 'Submit',

    [string]$JobId = '',

    [ValidateNotNullOrEmpty()]
    [string]$EulerHost = 'euler.ethz.ch',

    [ValidateNotNullOrEmpty()]
    [string]$GitBranch = 'agent/celegans-jm105-port',

    [ValidateNotNullOrEmpty()]
    [string]$RemoteRepoName = 'Jordan-McCarthy-celegans-analysis',

    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$RemoteResultsSubdir = 'JM105_CELEGANS_NMD_DR',

    [string]$NcbiEmail = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-BashSingleQuoted {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    return "'" + $Value.Replace("'", "'\"'\"'") + "'"
}

function Invoke-EulerBash {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Target,

        [Parameter(Mandatory = $true)]
        [string]$Script
    )

    $output = $Script | & ssh $Target 'bash -s' 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        $joined = ($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
        throw "Euler command failed with exit code $exitCode.`n$joined"
    }
    return @($output)
}

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    throw 'OpenSSH client was not found. Enable the Windows OpenSSH Client feature before running this script.'
}

$target = "$EulerUser@$EulerHost"

if ($Action -eq 'Status') {
    if ($JobId -notmatch '^\d+(?:_[0-9]+)?$') {
        throw 'For -Action Status, -JobId must be a numeric Slurm job ID, optionally followed by an array task suffix.'
    }

    $jobIdQuoted = ConvertTo-BashSingleQuoted -Value $JobId
    $statusScript = @"
set -euo pipefail
JOB_ID=$jobIdQuoted
sacct -j "`$JOB_ID" --format=JobID,JobName%24,State,ExitCode,Elapsed,MaxRSS,Start,End --units=G
printf '\nExpected latest output symlink:\n%s\n' "`$SCRATCH/JM105_CELEGANS_NMD_DR/step01_latest"
"@
    $statusOutput = Invoke-EulerBash -Target $target -Script $statusScript
    $statusOutput | ForEach-Object { Write-Host $_ }
    exit 0
}

$branchQuoted = ConvertTo-BashSingleQuoted -Value $GitBranch
$repoNameQuoted = ConvertTo-BashSingleQuoted -Value $RemoteRepoName
$resultsSubdirQuoted = ConvertTo-BashSingleQuoted -Value $RemoteResultsSubdir
$emailQuoted = ConvertTo-BashSingleQuoted -Value $NcbiEmail

$remoteTemplate = @'
set -euo pipefail

BRANCH=__BRANCH__
REPO_NAME=__REPO_NAME__
RESULTS_SUBDIR=__RESULTS_SUBDIR__
NCBI_EMAIL_VALUE=__NCBI_EMAIL__
REPO_URL='git@github.com:jorddyk/Jordan-McCarthy.git'
REPO_DIR="${HOME}/${REPO_NAME}"
RESULTS_ROOT="${SCRATCH:?SCRATCH is not set on Euler}/${RESULTS_SUBDIR}"
STEP_DIR="${REPO_DIR}/projects/jm105-intronsaurus/celegans-jm105-port/step01-metadata-audit"
SBATCH_SCRIPT="${STEP_DIR}/run_step01_metadata_audit.sbatch"

if ! command -v git >/dev/null 2>&1; then
    echo 'ERROR: git is not available on Euler PATH.' >&2
    exit 20
fi
if ! command -v sbatch >/dev/null 2>&1; then
    echo 'ERROR: sbatch is not available on Euler PATH.' >&2
    exit 21
fi

if [[ ! -d "${REPO_DIR}/.git" ]]; then
    git clone --branch "${BRANCH}" --single-branch "${REPO_URL}" "${REPO_DIR}"
else
    cd "${REPO_DIR}"
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "ERROR: dedicated Euler checkout is dirty: ${REPO_DIR}" >&2
        git status --short >&2
        exit 22
    fi
    ACTUAL_ORIGIN="$(git remote get-url origin)"
    if [[ "${ACTUAL_ORIGIN}" != "${REPO_URL}" && "${ACTUAL_ORIGIN}" != 'https://github.com/jorddyk/Jordan-McCarthy.git' ]]; then
        echo "ERROR: unexpected origin in ${REPO_DIR}: ${ACTUAL_ORIGIN}" >&2
        exit 23
    fi
    git fetch --prune origin "${BRANCH}"
    git checkout "${BRANCH}"
    git pull --ff-only origin "${BRANCH}"
fi

if [[ ! -f "${SBATCH_SCRIPT}" ]]; then
    echo "ERROR: Step 1 sbatch script is missing after GitHub update: ${SBATCH_SCRIPT}" >&2
    exit 24
fi

mkdir -p "${RESULTS_ROOT}"
cd "${RESULTS_ROOT}"
export JM105_CELEGANS_ROOT="${RESULTS_ROOT}"
export NCBI_EMAIL="${NCBI_EMAIL_VALUE}"

JOB_ID="$(sbatch --parsable "${SBATCH_SCRIPT}")"
COMMIT_SHA="$(git -C "${REPO_DIR}" rev-parse HEAD)"

printf 'JOB_ID=%s\n' "${JOB_ID}"
printf 'GIT_BRANCH=%s\n' "${BRANCH}"
printf 'GIT_COMMIT=%s\n' "${COMMIT_SHA}"
printf 'RESULTS_ROOT=%s\n' "${RESULTS_ROOT}"
printf 'LATEST_LINK=%s\n' "${RESULTS_ROOT}/step01_latest"
'@

$remoteScript = $remoteTemplate
$remoteScript = $remoteScript.Replace('__BRANCH__', $branchQuoted)
$remoteScript = $remoteScript.Replace('__REPO_NAME__', $repoNameQuoted)
$remoteScript = $remoteScript.Replace('__RESULTS_SUBDIR__', $resultsSubdirQuoted)
$remoteScript = $remoteScript.Replace('__NCBI_EMAIL__', $emailQuoted)

$submissionOutput = Invoke-EulerBash -Target $target -Script $remoteScript
$submissionOutput | ForEach-Object { Write-Host $_ }

$values = @{}
foreach ($line in $submissionOutput) {
    $text = $line.ToString()
    if ($text -match '^([A-Z_]+)=(.*)$') {
        $values[$Matches[1]] = $Matches[2]
    }
}

if (-not $values.ContainsKey('JOB_ID')) {
    throw 'Submission completed without returning a JOB_ID.'
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$recordPath = Join-Path -Path (Get-Location) -ChildPath "step01_submission_${timestamp}.json"
$record = [ordered]@{
    submitted_at_local = (Get-Date).ToString('o')
    euler_target = $target
    action = $Action
    job_id = $values['JOB_ID']
    git_branch = $values['GIT_BRANCH']
    git_commit = $values['GIT_COMMIT']
    results_root = $values['RESULTS_ROOT']
    latest_link = $values['LATEST_LINK']
}
$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $recordPath -Encoding utf8

Write-Host "Submission record: $recordPath"
Write-Host "Check status with:"
Write-Host ".\submit_step01_from_windows.ps1 -EulerUser '$EulerUser' -Action Status -JobId '$($values['JOB_ID'])'"
