# Work-Ahead Lanes — Pass 4 Multi-Mega-Train

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## WA-01: OCR Reflection Completion

When `Aspose.AI.LLM` becomes available on NuGet.org, run full reflection to confirm NO_LOWCODE.
Currently classified NO_LOWCODE_CONFIRMED via direct DLL reflection workaround.

## WA-02: PSD Reflection Completion

When `Aspose.JavaAttributes` becomes available on NuGet.org, run full reflection to confirm NO_LOWCODE.
Currently classified NO_LOWCODE_CONFIRMED via direct DLL reflection workaround.

## WA-03: words-mail-merger API Gap

If Aspose.Words LowCode MailMerger gains a simple one-call overload in a future release, implement
and replace the current stub. Track via words version monitoring.

## WA-04: PDF pdf-aconverter Deduplication

`pdf-aconverter` appears in both pr7 and pr10. When PR is created, only one version should be
published. The pr10 version (template-repaired) is authoritative. pr7 version is superseded.

## WA-05: Publication Gate

When PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR is set:
1. Create PR branches: `lowcode-examples-<family>-readme-io-final`
2. Target repos: aspose-{cells,words,pdf,diagram,email,slides}-net/Aspose.{Family}.LowCode-for-.NET-Examples
3. Use GH_TOKEN (41 chars, available)
4. All 41 PR candidates ready for merge
