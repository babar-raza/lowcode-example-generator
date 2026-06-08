# Words OFD Blocker Packet

**Sprint**: lowcode-true-closure-20260531

## Classification
UNSUPPORTED_FORMAT_BLOCKER

## Evidence
- Runtime: `System.ArgumentException: Invalid save format requested`
- Probe: `workspace/runs/blocker-closure-20260531/probes/words-ofd/`
- OFD is not in Aspose.Words LowCode SaveFormat enum

## Not a Fixture Issue
OFD is an OUTPUT format target, not an input fixture requirement.
The failure is in the Words LowCode library's format support.

## Retry Condition
Requires Aspose.Words to implement OFD output in SaveFormat.
