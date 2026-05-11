# PDF PR #1 Pre-Merge Clean Checkout Validation

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/pdf-pr1-pre-merge-clean-checkout-validation.json`
**Verdict:** GATE_2_PASS

## Clone

- Source: `aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples`
- Branch: `plugin-examples/pdf/20260506-083146`
- Method: `git clone --depth 1` into isolated temp directory

## Results

| Example | Restore | Build | Run | Output | API |
|---|---|---|---|---|---|
| merger | PASS | PASS (0W 0E) | PASS | output.pdf 56346 bytes, %PDF header | Merger.Process(MergeOptions) |
| text-extractor | PASS | PASS (0W 0E) | PASS | Text extracted (eval watermark) | TextExtractor.Process(TextExtractorOptions) |

- No TextAbsorber usage — correct LowCode API confirmed
- No splitter or optimizer in checkout
- No failed or backlogged examples present
