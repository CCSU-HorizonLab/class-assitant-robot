# PowerShell validation script to verify the clean repository structure.
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path (Split-Path $MyInvocation.MyCommand.Path -Parent) -Parent
$LocalDir = Join-Path $RepoRoot "local_analysis_client"

Write-Host "=== Starting Clean Structure Validation (PowerShell) ===" -ForegroundColor Cyan

# 1. Verify legacy wrappers do NOT exist
Write-Host "[Step 1] Verifying legacy wrapper files are deleted..." -ForegroundColor Gray
$Wrappers = @(
    "classroom_feedback_pipeline.py",
    "yolo_interaction_processor.py",
    "keyframe_receiver.py",
    "build_interaction_dataset.py",
    "train_interaction_model.py"
)
foreach ($wrapper in $Wrappers) {
    $wrapperPath = Join-Path $LocalDir $wrapper
    if (Test-Path -LiteralPath $wrapperPath) {
        Write-Error "Error: Legacy wrapper still exists: $wrapperPath"
        exit 1
    }
}
Write-Host "  - All legacy wrapper files are clean. [OK]" -ForegroundColor Green

# 2. Verify dead YAML configurations do NOT exist
Write-Host "[Step 2] Verifying dead configs are deleted..." -ForegroundColor Gray
$DeadConfigs = @(
    "configs/base.yaml",
    "configs/base.example.yaml",
    "configs/cloud.yaml",
    "configs/pi-edge.yaml"
)
foreach ($config in $DeadConfigs) {
    $configPath = Join-Path $LocalDir $config
    if (Test-Path -LiteralPath $configPath) {
        Write-Error "Error: Legacy configuration still exists: $configPath"
        exit 1
    }
}
Write-Host "  - All legacy configurations are clean. [OK]" -ForegroundColor Green

# 3. Verify core files compile successfully
Write-Host "[Step 3] Verifying core modules compile..." -ForegroundColor Gray
$PythonExe = Join-Path $RepoRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$CoreFiles = @(
    "local-processor/core/classroom_feedback_pipeline.py",
    "local-processor/core/yolo_interaction_processor.py",
    "local-processor/api/keyframe_receiver.py"
)
foreach ($file in $CoreFiles) {
    $filePath = Join-Path $LocalDir $file
    & $PythonExe -B -m py_compile $filePath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error: Python compilation failed for $filePath"
        exit 1
    }
}
Write-Host "  - All core files compiled successfully. [OK]" -ForegroundColor Green

# 4. Run end-to-end pipeline validation
Write-Host "[Step 4] Running end-to-end pipeline test..." -ForegroundColor Gray
$PipelineTest = Join-Path $LocalDir "local-processor/scripts/validate_delivery_package_pipeline.py"
& $PythonExe $PipelineTest
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Pipeline validation test failed."
    exit 1
}
Write-Host "  - Pipeline validation test passed. [OK]" -ForegroundColor Green

Write-Host "=== Validation Successful! Codebase is Clean and Operational ===" -ForegroundColor Green
exit 0
