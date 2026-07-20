# ==============================================================================
# V3 Phase 3.20 Validation Script: Local Analyzer Structure Progressive Refinement
# ==============================================================================
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()

Write-Host "=== Starting Phase 3.20 Validation (PowerShell) ==="

$LocalDir = "local_analysis_client"
$Wrappers = @(
    "classroom_feedback_pipeline.py",
    "yolo_interaction_processor.py",
    "keyframe_receiver.py",
    "build_interaction_dataset.py",
    "train_interaction_model.py"
)

# 1. Check wrappers for warning comment headers
Write-Host "[Step 1] Checking warning comments in root wrappers..."
foreach ($wrapper in $Wrappers) {
    $wrapperPath = Join-Path $LocalDir $wrapper
    if (-not (Test-Path -LiteralPath $wrapperPath)) {
        Write-Error "Error: Wrapper file not found: $wrapperPath"
        exit 1
    }
    
    $content = Get-Content -LiteralPath $wrapperPath -Raw
    if ($content -notmatch "⚠️ WARNING") {
        Write-Error "Error: Wrapper file $wrapperPath is missing the warning header."
        exit 1
    }
    Write-Host "  - $wrapper contains warning header [OK]"
}

# 2. Check relocated script path
Write-Host "[Step 2] Checking relocated script paths..."
$OldScriptPath = Join-Path $LocalDir "show_5_3_test_result_for_screenshot.ps1"
$NewScriptPath = Join-Path $LocalDir "local-processor/scripts/show_5_3_test_result_for_screenshot.ps1"

if (Test-Path -LiteralPath $OldScriptPath) {
    Write-Error "Error: Script still exists at old path: $OldScriptPath"
    exit 1
}
Write-Host "  - Old script path is clean [OK]"

if (-not (Test-Path -LiteralPath $NewScriptPath)) {
    Write-Error "Error: Relocated script not found at: $NewScriptPath"
    exit 1
}
Write-Host "  - Relocated script present at new path [OK]"

# 3. Compile check
Write-Host "[Step 3] Performing python compile check on wrapper files..."
$PythonPath = "python"
if (Test-Path -LiteralPath "venv/Scripts/python.exe") {
    $PythonPath = "venv/Scripts/python.exe"
}
Write-Host "  - Using python: $PythonPath"

&$PythonPath -B -m py_compile `
    (Join-Path $LocalDir "classroom_feedback_pipeline.py") `
    (Join-Path $LocalDir "yolo_interaction_processor.py") `
    (Join-Path $LocalDir "keyframe_receiver.py") `
    (Join-Path $LocalDir "build_interaction_dataset.py") `
    (Join-Path $LocalDir "train_interaction_model.py")

Write-Host "  - Compilation successful [OK]"

# 4. Dry-run dynamic loading regression check
Write-Host "[Step 4] Performing dynamic loading regression check..."
&$PythonPath -c @"
import sys
sys.path.append('${LocalDir}')
import classroom_feedback_pipeline
import yolo_interaction_processor
import keyframe_receiver
import build_interaction_dataset
import train_interaction_model
print('  - Dynamic imports check passed [OK]')
"@


Write-Host "=== Phase 3.20 Validation Successful! ==="
Write-Host "PHASE320_LOCAL_STRUCTURE_REFINED=true"
Write-Host "PHASE320_WRAPPERS_WARNING_HEADER_OK=true"
Write-Host "PHASE320_RELOCATION_OK=true"
Write-Host "PHASE320_COMPILATION_OK=true"
Write-Host "PHASE320_DYNAMIC_LOAD_REGRESSION_OK=true"
