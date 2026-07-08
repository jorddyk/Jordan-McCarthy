# Purpose: Windows PowerShell helper for Intronsaurus vNext3Y matched RNA/protein Gene Stories workflow.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-23; recovered bundle `Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`.
# Expected inputs: Local bundle files in `$HOME\Downloads\Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`, SSH/SCP access to `jmccarthy@euler.ethz.ch`.
# Expected outputs: Upload/submit or retrieval of vNext3Y Euler outputs to Jordan's Windows `Y:\Jordan\JM101\...` folder.
# Known assumptions: Uses Windows OpenSSH `ssh`/`scp`; does not commit raw biological data.
# Data status: Administrative helper only; no fake biological data.
$ErrorActionPreference = "Continue"

$Remote = "jmccarthy@euler.ethz.ch"
$Project = "/cluster/scratch/jmccarthy/JM105_RNAseq"
$RunName = "121_INTRONSAURUS_GENE_STORIES_SINGLE_ENTRY_V3Y"
$Dest = "Y:\Jordan\JM101\Intronsaurus_Matched_RNA_Protein_Gene_Stories_vNext3Y\$RunName"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

scp "${Remote}:${Project}/${RunName}.tar.gz" "$Dest\"
scp "${Remote}:${Project}/${RunName}.tar.gz.sha256" "$Dest\"
scp "${Remote}:${Project}/${RunName}/interactive/Intronsaurus_Explore_Restored_vNext3Y.html" "$Dest\"
scp "${Remote}:${Project}/${RunName}/interactive/Intronsaurus_Aging_RNA_Fate_Atlas_vNext3Y.html" "$Dest\"
scp "${Remote}:${Project}/${RunName}/interactive/Intronsaurus_Explore_Restored_vNext3M_PROTECTED_COPY.html" "$Dest\"
scp "${Remote}:${Project}/${RunName}/qc/Intronsaurus_vNext3Y_validation_report.json" "$Dest\"
scp "${Remote}:${Project}/${RunName}/qc/Intronsaurus_vNext3Y_Sun_sanity_examples.csv" "$Dest\"
scp "${Remote}:${Project}/${RunName}/tables/Sun_2021_PXD018917_processed_proteomics_v3Y.csv" "$Dest\"
scp "${Remote}:${Project}/${RunName}/tables/Sun_2021_PXD018917_processed_proteomics.csv" "$Dest\"
scp "${Remote}:${Project}/${RunName}/tables/Intronsaurus_vNext3Y_Sun_proteomics_story_matches.csv" "$Dest\"

Write-Host ""
Write-Host "Downloaded to:"
Write-Host $Dest
Write-Host ""
Write-Host "Open this HTML:"
Write-Host "$Dest\Intronsaurus_Explore_Restored_vNext3Y.html"
Write-Host ""
Write-Host "Validation:"
Get-Content "$Dest\Intronsaurus_vNext3Y_validation_report.json"
