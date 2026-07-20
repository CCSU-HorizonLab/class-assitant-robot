# V3 Phase 3.20 Tasks: Local Analyzer Structure Progressive Refinement

## Task 1: Prepend Warning Headers to Root-level Dynamic Wrappers

- Modify the following 5 files in `local_analysis_client/`:
  - `classroom_feedback_pipeline.py`
  - `yolo_interaction_processor.py`
  - `keyframe_receiver.py`
  - `build_interaction_dataset.py`
  - `train_interaction_model.py`
- Prepend the standard block comment warning to clearly label them as backward-compatibility wrappers.
- Keep the dynamic importing code block below the warning exactly intact.

Acceptance:
- Each wrapper contains the warning block comment.
- All wrapper files compile successfully using Python's `py_compile`.

## Task 2: Relocate Stray Screenshot/Debug Script

- Relocate `local_analysis_client/show_5_3_test_result_for_screenshot.ps1` to `local_analysis_client/local-processor/scripts/show_5_3_test_result_for_screenshot.ps1`.
- Clean up the original root file.

Acceptance:
- The script is present in `local-processor/scripts/`.
- The original script is removed from the root directory of `local_analysis_client/`.

## Task 3: Create Validation Script

- Create `scripts/validate_phase3_20_local_structure.sh` in the workspace root.
- The script must verify:
  - Warning block headers are present in the 5 wrapper files.
  - Dynamic importing blocks are intact.
  - The script `show_5_3_test_result_for_screenshot.ps1` is present at its new path and absent in the old path.
  - Dynamic loading wrapper regression checks (verify that importing doesn't fail).

Acceptance:
- Validation script is runnable.
- It produces clear output markers, culminating in `PHASE320_LOCAL_STRUCTURE_REFINED=true`.

## Task 4: Run Validation and Update Status

- Execute the validation script.
- Verify status of all markers.
- Create `docs/project-status/v3-phase3.20-local-structure-progressive-refinement.md` detailing the validation markers.

Final marker:
```text
PHASE320_LOCAL_STRUCTURE_REFINED=true
```
