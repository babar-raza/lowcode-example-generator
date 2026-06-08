# Words Processor Blocker Packet

**Sprint**: lowcode-true-closure-20260531

## Classification
PERMANENTLY_BLOCKED — ABSTRACT_BASE_CLASS

## Evidence
- `Aspose.Words.LowCode.Processor` has 0 public constructors (INTERNAL)
- All methods (From, To, Execute) are instance methods
- CS1729: `new Processor()` — no accessible constructor
- CS0120: `Processor.From(...)` — non-static member in static context
- Reflection probe: `workspace/runs/blocker-closure-20260531/probes/reflect/`

## Retry Condition
Requires Aspose.Words to add a public static factory method or public constructor.
