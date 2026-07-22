$ErrorActionPreference = "Stop"

$Python = "python"
$Config = "configs/final_candidate_r04.yaml"
$Manifest = "data/manifests/manifest.csv"
$ExperimentOutput = "outputs/final_candidate_r04/experiments"
$AnalysisOutput = "outputs/final_candidate_r04/analysis"

& $Python scripts/03_run_batch.py `
  --config $Config `
  --manifest $Manifest `
  --output-dir $ExperimentOutput `
  --dataset DRIVE `
  --dataset STARE `
  --dataset CHASEDB1

& $Python scripts/04_summarize_results.py `
  --config $Config `
  --results "$ExperimentOutput/metrics_per_image.csv" `
  --output-dir $AnalysisOutput `
  --dataset DRIVE `
  --dataset STARE `
  --dataset CHASEDB1

Write-Host "Final candidate experiment completed."
Write-Host "Metrics : $ExperimentOutput/metrics_per_image.csv"
Write-Host "Analysis: $AnalysisOutput"