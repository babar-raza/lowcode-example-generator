# Words OFD Final Classification

## Investigation
OFD (Open Fixed-layout Document) is a format not supported by Aspose.Words LowCode Converter.

## Evidence (from previous sprint, ACCEPTED)
- Aspose.Words.LowCode.Converter does not list OFD as a supported SaveFormat
- No OFD-related SaveFormat enum value exists in the Words API
- OFD is a Chinese government standard — niche format not in Words scope

## Classification: PERMANENTLY_BLOCKED — UNSUPPORTED_FORMAT
Not a missing fixture or implementation gap — the format is simply not supported by the API.

## Completion Queue
Listed as BACKLOGGED with reason "PILOT_SCOPE_DEFERRED: OFD format fixture not available"
Should be reclassified to PERMANENTLY_BLOCKED: UNSUPPORTED_FORMAT.

Note: "pdf-ofd" in the queue is actually a PDF family entry, not words.
The PDF LowCode API also doesn't support OFD as an output format.

## Retry Condition
Re-test if Aspose adds OFD support in a future version.
