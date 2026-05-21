============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator
configfile: pyproject.toml
plugins: timeout-2.4.0
timeout: 30.0s
timeout method: thread
timeout func_only: False
collecting ... collected 19 items

tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_blocks_when_audit_has_failures PASSED [  5%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_blocks_when_audit_is_shallow PASSED [ 10%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_blocks_when_no_audit_artifact PASSED [ 15%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_emergency_override_bypasses_failed_audit PASSED [ 21%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_emergency_override_records_evidence PASSED [ 26%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_env_var_approval_does_not_bypass_failed_audit PASSED [ 31%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_normal_approval_does_not_bypass_failed_audit PASSED [ 36%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_override_not_used_when_audit_passes PASSED [ 42%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_passes_when_audit_is_content_based_and_all_pass PASSED [ 47%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_wrong_approval_token_does_not_bypass PASSED [ 52%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_gate_blocks_when_audit_shallow PASSED [ 57%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_gate_blocks_when_no_audit_missing PASSED [ 63%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_gate_passes_with_valid_content_audit PASSED [ 68%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_normal_approval_plus_failed_audit_is_blocked PASSED [ 73%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_readme_gate_called_with_correct_family PASSED [ 78%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_check_readme_audit_gate_called_in_main PASSED [ 84%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_emergency_override_token_defined_in_gate PASSED [ 89%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_gate_passed_check_in_main PASSED [ 94%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_readme_audit_gate_imported_in_main PASSED [100%]

============================= 19 passed in 0.68s ==============================
