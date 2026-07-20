# V3 Phase 3.20 Spec: Local Analyzer Structure Progressive Refinement

## Goal

Phase 3.20 progressively refines the file structure and developer experience (DX) of the local analysis client (`local_analysis_client`). It aims to:
- Clearly label backward-compatibility wrapper files at the root level to prevent developers from accidentally editing them instead of the core implementation files.
- Relocate stray debugging/temporary scripts into appropriate subdirectories to keep the root workspace clean.
- Maintain strict backward compatibility with all existing calling commands, automated launchers, and validation scripts.

## Scope

Files and directories in scope:

- Root wrapper files in `local_analysis_client/`:
  - `classroom_feedback_pipeline.py`
  - `yolo_interaction_processor.py`
  - `keyframe_receiver.py`
  - `build_interaction_dataset.py`
  - `train_interaction_model.py`
- Stray scripts in `local_analysis_client/`:
  - `show_5_3_test_result_for_screenshot.ps1`
- Relocation target:
  - `local_analysis_client/local-processor/scripts/`

Allowed changes:
- Prepend a prominent block comment warning at the very top of each of the 5 wrapper files.
- Move `show_5_3_test_result_for_screenshot.ps1` into `local-processor/scripts/`.
- Create a validation script `scripts/validate_phase3_20_local_structure.sh`.

Forbidden changes:
- Do NOT modify the dynamic importing wrapper logic or system module injection code.
- Do NOT modify the core implementations under `local-processor/core/`, `local-processor/api/`, `local-processor/tools/`, or any other directory.
- Do NOT delete the wrapper files, as they are crucial for backward compatibility.
- No database, API, or Cloud backend changes.
- No `git add .` (only stage explicitly modified/relocated files).

## Warning Header Design

Each of the 5 wrapper files must have the following warning header prepended:

```python
# ==============================================================================
# ⚠️ WARNING: BACKWARD COMPATIBILITY WRAPPER / 向后兼容包装文件
# ==============================================================================
# 本文件仅作为向后兼容的动态导入包装层，供历史脚本和命令行入口直接调用。
# 请勿在此处修改任何实际业务逻辑或算法代码！
#
# 真实业务逻辑及核心代码请移步至以下路径修改：
# - classroom_feedback_pipeline.py -> local-processor/core/classroom_feedback_pipeline.py
# - yolo_interaction_processor.py  -> local-processor/core/yolo_interaction_processor.py
# - keyframe_receiver.py           -> local-processor/api/keyframe_receiver.py
# - build_interaction_dataset.py   -> local-processor/tools/build_interaction_dataset.py
# - train_interaction_model.py     -> local-processor/train/ (或对应训练路径)
# ==============================================================================
```

## Validation Plan

1. **Static compilation check**:
   ```bash
   python -B -m py_compile local_analysis_client/classroom_feedback_pipeline.py local_analysis_client/yolo_interaction_processor.py local_analysis_client/keyframe_receiver.py local_analysis_client/build_interaction_dataset.py local_analysis_client/train_interaction_model.py
   ```
2. **Path checks**:
   - Verify that `show_5_3_test_result_for_screenshot.ps1` is no longer in the root of `local_analysis_client/`.
   - Verify that `show_5_3_test_result_for_screenshot.ps1` is present in `local_analysis_client/local-processor/scripts/`.
3. **Automated validation script**:
   - Create `scripts/validate_phase3_20_local_structure.sh` to assert these conditions.
