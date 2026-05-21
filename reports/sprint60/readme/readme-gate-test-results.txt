============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator
configfile: pyproject.toml
plugins: timeout-2.4.0
timeout: 30.0s
timeout method: thread
timeout func_only: False
collecting ... collected 13 items

tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenNoAuditArtifact::test_gate_blocks_when_no_audit_artifact PASSED [  7%]
tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenNoAuditArtifact::test_gate_reports_family_in_result PASSED [ 15%]
tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenAuditIsShallow::test_gate_blocks_when_audit_is_shallow PASSED [ 23%]
tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenAuditHasFailedRecords::test_gate_blocks_when_audit_has_failed_records PASSED [ 30%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_approval_token_from_env_var PASSED [ 38%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_gate_passes_for_family_with_content_audit PASSED [ 46%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_gate_passes_with_content_based_audit PASSED [ 53%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_gate_passes_with_partial_content_audit_and_approval PASSED [ 61%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_content_audit_detection_with_fields PASSED [ 69%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_empty_records_not_content_based PASSED [ 76%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_mixed_records_detected_as_content_based PASSED [ 84%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_shallow_audit_detection_size_only PASSED [ 92%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_sprint59_readme_audit_detected_as_shallow PASSED [100%]

============================= 13 passed in 0.52s ==============================
