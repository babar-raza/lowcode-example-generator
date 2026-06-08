# Plugin-Code Registry Validator Tests Plan

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Test File Location

`tests/unit/test_plugin_code_registry_validator.py`

---

## Test Cases

### test_rule1_entry_requires_product_page
```python
def test_rule1_entry_requires_product_page():
    """REGISTRY_STATUS_NO_PRODUCT_PAGE: entry without products.aspose.net URL must fail."""
    entry = {
        "plugin_url": "https://example.com/not-aspose",
        "registry_status": "CODE_HARVESTED",
        "evidence_paths": ["x"], "history": [{"date":"2026-06-04","status":"CODE_HARVESTED","analyst_notes":"test"}],
        "next_action": "test", "implementation_model": "LOAD_SAVE_OPTIONS",
    }
    result = validate_entry(entry)
    assert "REGISTRY_STATUS_NO_PRODUCT_PAGE" in result.errors
```

### test_rule2_code_harvested_requires_hash
```python
def test_rule2_code_harvested_requires_hash():
    """CODE_HARVESTED_NO_CODE_HASH: CODE_HARVESTED entry without code_hashes must fail."""
    entry = make_valid_entry(registry_status="CODE_HARVESTED", code_hashes=[])
    result = validate_entry(entry)
    assert "CODE_HARVESTED_NO_CODE_HASH" in result.errors
```

### test_rule7_implementation_model_required
```python
def test_rule7_implementation_model_required():
    """IMPLEMENTATION_MODEL_MISSING: entry without implementation_model must fail."""
    entry = make_valid_entry(implementation_model=None)
    result = validate_entry(entry)
    assert "IMPLEMENTATION_MODEL_MISSING" in result.errors
```

### test_rule8_history_required
```python
def test_rule8_history_required():
    """HISTORY_RECORD_MISSING: entry without history must fail."""
    entry = make_valid_entry(history=[])
    result = validate_entry(entry)
    assert "HISTORY_RECORD_MISSING" in result.errors
```

### test_rule13_unverified_not_ready
```python
def test_rule13_unverified_not_ready():
    """UNVERIFIED_MARKED_READY: WEBSITE_PATTERN_UNVERIFIED entry as READY must fail."""
    entry = make_valid_entry(registry_status="WEBSITE_PATTERN_UNVERIFIED")
    entry["transformation_readiness"] = "READY_NEXT_SPRINT"
    result = validate_entry(entry)
    assert "UNVERIFIED_MARKED_READY" in result.errors
```

### test_valid_entry_passes
```python
def test_valid_entry_passes():
    """A complete, valid entry must pass all rules."""
    entry = {
        "family": "barcode",
        "plugin_slug": "generate-barcode",
        "plugin_url": "https://products.aspose.net/barcode/net/generate-barcode",
        "page_hash": "1770337e14ce0847",
        "registry_status": "CODE_HARVESTED",
        "implementation_model": "STATIC_CONVERTER_CLASS",
        "code_hashes": ["bc77bfce202fa6f5"],
        "blocker_type": None,
        "next_action": "Validate symbols against DllReflector",
        "evidence_paths": ["reports/.../crawl/plugin-page-inventory.json"],
        "history": [{"date": "2026-06-04", "status": "CODE_HARVESTED", "analyst_notes": "GitHub code fetched"}],
    }
    result = validate_entry(entry)
    assert not result.errors
```

---

## Implementation Location

`src/plugin_examples/evidence_validator/rules/plugin_code_registry.py`

Add to test runner: `tests/unit/test_plugin_code_registry_validator.py`
