# Purpose: Windows PowerShell helper for Intronsaurus vNext3Y matched RNA/protein Gene Stories workflow.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-23; recovered bundle `Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`.
# Expected inputs: Local bundle files in `$HOME\Downloads\Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`, SSH/SCP access to `jmccarthy@euler.ethz.ch`.
# Expected outputs: Upload/submit or retrieval of vNext3Y Euler outputs to Jordan's Windows `Y:\Jordan\JM101\...` folder.
# Known assumptions: Uses Windows OpenSSH `ssh`/`scp`; does not commit raw biological data.
# Data status: Administrative helper only; no fake biological data.
$ErrorActionPreference = "Stop"

$Remote = "jmccarthy@euler.ethz.ch"
$Project = "/cluster/scratch/jmccarthy/JM105_RNAseq"
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodeDir = "$Project/code/intronsaurus_vnext3Y_single_entry_gene_stories"
$InputDir = "$Project/input/intronsaurus_vnext3Y_single_entry_gene_stories"
$LogDir = "$Project/logs"

$Script = Join-Path $BundleDir "141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py"
$Sbatch = Join-Path $BundleDir "141_intronsaurus_matched_rna_protein_gene_stories_v3Y.sbatch"
$Check = Join-Path $BundleDir "check_intronsaurus_matched_rna_protein_gene_stories_v3Y_status.sh"
$SourceArchive = Join-Path $BundleDir "110_INTRONSAURUS_GENE_STORIES_PRECISE_INTERPRETER_V3M.tar.gz"
$SunXlsx = Join-Path $BundleDir "11357_2021_412_MOESM3_ESM.xlsx"

foreach ($f in @($Script,$Sbatch,$Check,$SourceArchive,$SunXlsx)) {
    if (!(Test-Path $f)) { throw "Missing required bundle file: $f" }
}

ssh $Remote "mkdir -p '$CodeDir' '$InputDir' '$LogDir'"
scp $Script "${Remote}:${CodeDir}/"
scp $Sbatch "${Remote}:${CodeDir}/"
scp $Check "${Remote}:${CodeDir}/"
scp $SourceArchive "${Remote}:${InputDir}/"
scp $SunXlsx "${Remote}:${InputDir}/"

Write-Host "Submitting v3Y matched RNA/protein Gene Stories on Euler..."
$SubmitOutput = ssh $Remote "sbatch '${CodeDir}/141_intronsaurus_matched_rna_protein_gene_stories_v3Y.sbatch'"
Write-Host $SubmitOutput

if ($SubmitOutput -match 'Submitted batch job\s+(\d+)') {
    $JobID = $Matches[1]
} else {
    throw "Could not parse SLURM job id from: $SubmitOutput"
}

ssh $Remote "printf '%s' '$JobID' > '$LogDir/intronsaurus_vnext3Y_latest_jobid.txt'"
Write-Host "Submitted JOBID=$JobID"
Write-Host "Check with: bash $CodeDir/check_intronsaurus_matched_rna_protein_gene_stories_v3Y_status.sh"
