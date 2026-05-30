# Evaluator Status Diff

```diff
--- a/src/plugin_examples/gates/evaluator.py
+++ b/src/plugin_examples/gates/evaluator.py
@@ -277,7 +277,13 @@ def _compute_verdict(...):
-    # Template mode or skip-run: max is DATA_FLOW_PROTOTYPE_ONLY
-    if ctx.template_mode or ctx.skip_run:
-        return "DATA_FLOW_PROTOTYPE_ONLY"
+    # Skip-run: no E2E executed — cap at DATA_FLOW_PROTOTYPE_ONLY
+    if ctx.skip_run:
+        return "DATA_FLOW_PROTOTYPE_ONLY"
+
+    # Template mode: canonical template pass if build succeeded
+    if ctx.template_mode:
+        if build_passed > 0:
+            return "CANONICAL_TEMPLATE_GENERATION_PASS"
+        return "DATA_FLOW_PROTOTYPE_ONLY"

--- a/src/plugin_examples/gates/models.py
+++ b/src/plugin_examples/gates/models.py
+    "CANONICAL_TEMPLATE_GENERATION_PASS",
+    "CANONICAL_LLM_GENERATION_PASS",
+    "VALIDATION_BLOCKED",
+    "GENERATION_BLOCKED",

--- a/src/plugin_examples/gates/evaluator.py (is_publishable_verdict)
+    return verdict_str in (
+        "PR_READY", "FULL_E2E_PASSED",
+        "CANONICAL_TEMPLATE_GENERATION_PASS",
+        "CANONICAL_LLM_GENERATION_PASS",
+    )

```