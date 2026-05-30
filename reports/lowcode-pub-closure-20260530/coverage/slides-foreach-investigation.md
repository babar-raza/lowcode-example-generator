# Slides ForEach Investigation — lowcode-pub-closure-20260530

## API: Aspose.Slides.LowCode.ForEach

### Reflection analysis
ForEach is a utility/helper class providing iteration over slide elements.
It does not implement a standalone pipeline workflow.
It is a SUPPORTING CLASS, not an operation root.

### Usage pattern
```csharp
ForEach.Presentation(pres, (slide, idx) => { /* process slide */ });
```
It wraps a callback — cannot produce a meaningful standalone output.

### Classification: NON_RUNNABLE_HELPER
