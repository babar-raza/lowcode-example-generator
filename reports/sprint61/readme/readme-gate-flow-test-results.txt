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

tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_approval_bypass_overrides_failed_audit PASSED [  7%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_blocks_when_audit_has_failures PASSED [ 14%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_blocks_when_audit_is_shallow PASSED [ 21%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_blocks_when_no_audit_artifact PASSED [ 28%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_env_var_approval_bypass PASSED [ 35%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_passes_when_audit_is_content_based_and_all_pass PASSED [ 42%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeAuditGateUnit::test_wrong_approval_token_does_not_bypass PASSED [ 50%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_gate_blocks_when_audit_shallow PASSED [ 57%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_gate_blocks_when_no_audit_missing PASSED [ 64%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_gate_passes_with_valid_content_audit PASSED [ 71%]
tests/unit/test_publish_pr_readme_gate.py::TestPublishPrReadmeGateWiring::test_readme_gate_called_with_correct_family PASSED [ 78%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_check_readme_audit_gate_called_in_main PASSED [ 85%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_gate_passed_check_in_main PASSED [ 92%]
tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy::test_readme_audit_gate_imported_in_main PASSED [100%]

============================= 14 passed in 0.54s ==============================
