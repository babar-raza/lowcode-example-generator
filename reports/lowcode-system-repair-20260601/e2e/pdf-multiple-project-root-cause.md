# PDF Multiple-Project-File Root Cause Analysis

## Issue
9 PDF examples previously failed with MSB1011:
> Specify which project or solution file to use because this folder contains more than one project or solution file.

## Root Cause
Example directories contained both a non-prefixed csproj (e.g., `doc-converter.csproj`) and a canonical prefixed csproj (e.g., `pdf-doc-converter.csproj`). The non-prefixed files were untracked artifacts from prior generation runs.

## Fix Applied (Previous Sprint)
The 9 duplicate non-prefixed csproj files were deleted:
- pdf-controlled-pilot/doc-converter/doc-converter.csproj
- pdf-controlled-pilot/html/html.csproj
- pdf-controlled-pilot/xls-converter/xls-converter.csproj
- pdf-controlled-pilot-pr5/jpeg/jpeg.csproj
- pdf-controlled-pilot-pr5/png/png.csproj
- pdf-controlled-pilot-pr5/tiff/tiff.csproj
- pdf-controlled-pilot-pr6/image-extractor/image-extractor.csproj
- pdf-controlled-pilot-pr6/table-generator/table-generator.csproj
- pdf-controlled-pilot-pr6/toc-generator/toc-generator.csproj

## Current Status
All PDF example directories have exactly 1 csproj file.
E2E: 49/49 PASS — no MSB1011 errors.

## Prevention
Validator added: fail if any example directory has >1 csproj file.
