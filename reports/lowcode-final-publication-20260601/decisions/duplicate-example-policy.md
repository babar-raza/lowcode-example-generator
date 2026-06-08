# Duplicate Example Policy

## Definition
A duplicate example is a generated example whose Program.cs is functionally identical to another example already published under a different directory name.

## Identification Method
1. Compare Program.cs content across all examples in a family.
2. If two examples demonstrate the same LowCode type with the same operations, the one matching the format-authority contract name is canonical; the other is duplicate.

## Action: EXCLUDE_DUPLICATE
Duplicates are excluded from publication. They are not packaged, not counted in any denominator, and not included in PR branches.

## Current Duplicates
| Duplicate | Canonical Original | Family |
|-----------|-------------------|--------|
| slides/slides-compress | slides/compress | slides |
| slides/slides-convert | slides/convert | slides |
| slides/slides-merger | slides/merger | slides |
| email/email-converter | email/converter | email |

## Root Cause
Generator produced both prefixed (`slides-slides-*`) and unprefixed (`slides-*`) directory names. The unprefixed versions match format-authority contract names and are canonical.

## Decision Authority
Agent-delegated per sprint `lowcode-final-publication-20260601`.
