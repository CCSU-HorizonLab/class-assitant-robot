#!/usr/bin/env bash
# ==============================================================================
# V3 Phase 3.20 Validation Script: Local Analyzer Structure Progressive Refinement
# ==============================================================================
set -euo pipefail

echo "=== Starting Phase 3.20 Validation ==="

# Define paths
LOCAL_DIR="local_analysis_client"
WRAPPERS=(
    "classroom_feedback_pipeline.py"
    "yolo_interaction_processor.py"
    "keyframe_receiver.py"
    "build_interaction_dataset.py"
    "train_interaction_model.py"
)

# 1. Check wrappers for warning comment headers
echo "[Step 1] Checking warning comments in root wrappers..."
for wrapper in "${WRAPPERS[@]}"; do
    wrapper_path="${LOCAL_DIR}/${wrapper}"
    if [ ! -f "${wrapper_path}" ]; then
        echo "Error: Wrapper file not found: ${wrapper_path}"
        exit 1
    fi
    
    # Check for warning pattern
    if ! grep -q "⚠️ WARNING" "${wrapper_path}"; then
        echo "Error: Wrapper file ${wrapper_path} is missing the warning header."
        exit 1
    fi
    echo "  - ${wrapper} contains warning header [OK]"
done

# 2. Check relocated script path
echo "[Step 2] Checking relocated script paths..."
OLD_SCRIPT_PATH="${LOCAL_DIR}/show_5_3_test_result_for_screenshot.ps1"
NEW_SCRIPT_PATH="${LOCAL_DIR}/local-processor/scripts/show_5_3_test_result_for_screenshot.ps1"

if [ -f "${OLD_SCRIPT_PATH}" ]; then
    echo "Error: Script still exists at old path: ${OLD_SCRIPT_PATH}"
    exit 1
fi
echo "  - Old script path is clean [OK]"

if [ ! -f "${NEW_SCRIPT_PATH}" ]; then
    echo "Error: Relocated script not found at: ${NEW_SCRIPT_PATH}"
    exit 1
fi
echo "  - Relocated script present at new path [OK]"

# 3. Compile check
echo "[Step 3] Performing python compile check on wrapper files..."
python -B -m py_compile \
    "${LOCAL_DIR}/classroom_feedback_pipeline.py" \
    "${LOCAL_DIR}/yolo_interaction_processor.py" \
    "${LOCAL_DIR}/keyframe_receiver.py" \
    "${LOCAL_DIR}/build_interaction_dataset.py" \
    "${LOCAL_DIR}/train_interaction_model.py"

echo "  - Compilation successful [OK]"

# 4. Dry-run dynamic loading regression check (import wrappers to ensure they don't throw exception)
echo "[Step 4] Performing dynamic loading regression check..."
python -c "
import sys
sys.path.append('${LOCAL_DIR}')
import classroom_feedback_pipeline
import yolo_interaction_processor
import keyframe_receiver
import build_interaction_dataset
import train_interaction_model
print('  - Dynamic imports check passed [OK]')
"

echo "=== Phase 3.20 Validation Successful! ==="
echo "PHASE320_LOCAL_STRUCTURE_REFINED=true"
echo "PHASE320_WRAPPERS_WARNING_HEADER_OK=true"
echo "PHASE320_RELOCATION_OK=true"
echo "PHASE320_COMPILATION_OK=true"
echo "PHASE320_DYNAMIC_LOAD_REGRESSION_OK=true"
