# Lane C: Words Processor API Investigation Report

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20

## Classification: PERMANENTLY_BLOCKED

## Evidence

### 1. Portfolio Action Planner Registry
In `src/plugin_examples/portfolio_action_planner.py` line 59:
```python
PERMANENTLY_BLOCKED = {
    "pdf/Timestamp": "External TSA ServerUrl required",
    "pdf/Ofd": "OFD input format, no programmatic fixture",
    "words/Processor": "No public constructor, no static entrypoint (CS1729+CS0120)",
}
```

### 2. API Analysis
- **CS1729:** `Aspose.Words.LowCode.Processor` has no public parameterless constructor
- **CS0120:** Non-static Process() method cannot be called without an instance
- No factory method, no builder pattern, no public constructor available
- Words LowCode namespace does not expose any instantiation path for Processor

### 3. FormatContract Authority
The FormatContract store contains 8 Words types. **Processor is NOT among them:**
- Converter, Merger, Splitter, Comparer, MailMerger, ReportBuilder, Watermarker, Replacer

This confirms the API discovery excluded Processor from the runnable set.

### 4. Current Portfolio State
- Words: 8/8 pilot complete (all non-Processor types)
- Processor: permanently_blocked since initial discovery
- No new Aspose.Words release changes this status

## Retest Trigger
- Aspose.Words LowCode adds public constructor or static factory for Processor
- New Aspose.Words NuGet version with API change
- Manual user override with evidence

## Verdict
**permanently_blocked** — No public constructor, no static entrypoint (CS1729+CS0120).
Words portfolio remains at 8/8 complete for all runnable types.
