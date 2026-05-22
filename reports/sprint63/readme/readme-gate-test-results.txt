============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator
configfile: pyproject.toml
plugins: timeout-2.4.0
timeout: 30.0s
timeout method: thread
timeout func_only: False
collecting ... collected 14 items

tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenNoAuditArtifact::test_gate_blocks_when_no_audit_artifact PASSED [  7%]
tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenNoAuditArtifact::test_gate_reports_family_in_result PASSED [ 14%]
tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenAuditIsShallow::test_gate_blocks_when_audit_is_shallow PASSED [ 21%]
tests/unit/test_readme_audit_gate.py::TestGateBlocksWhenAuditHasFailedRecords::test_gate_blocks_when_audit_has_failed_records PASSED [ 28%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_emergency_override_bypasses_failed_audit PASSED [ 35%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_env_var_approval_does_not_bypass_failed_audit PASSED [ 42%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_gate_passes_for_family_with_content_audit PASSED [ 50%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_gate_passes_with_content_based_audit PASSED [ 57%]
tests/unit/test_readme_audit_gate.py::TestGatePassesWithContentAudit::test_normal_approval_does_not_bypass_failed_audit PASSED [ 64%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_content_audit_detection_with_fields PASSED [ 71%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_empty_records_not_content_based PASSED [ 78%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_mixed_records_detected_as_content_based PASSED [ 85%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_shallow_audit_detection_size_only PASSED [ 92%]
tests/unit/test_readme_audit_gate.py::TestShallowAuditDetection::test_sprint59_readme_audit_detected_as_shallow PASSED [100%]

============================= 14 passed in 0.53s ==============================
