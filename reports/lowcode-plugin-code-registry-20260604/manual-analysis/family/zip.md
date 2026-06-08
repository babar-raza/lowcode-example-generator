# Family Manual Analysis: zip

## Date: 2026-06-04
## Evidence: GitHub repo aspose-zip/Aspose.ZIP-for-.NET, code: CompressToTarBz2.cs, CompressDirectory.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Archive class for ZIP; specialized classes for other formats.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Archive` — standard ZIP archives (Aspose.Zip)
- `TarArchive` — TAR archives
- `Bzip2Archive` — BZIP2 archives
- `GzipArchive` — GZIP archives
- `SevenZipArchive` — 7-Zip archives

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. Archive constructor + Save(stream) or ExtractAll(dir).
## 7. Document Object Model Workflow? No.
## 8. Recognition/Extraction APIs? Yes. ExtractAll() and ExtractToDirectory() for decompression.
## 9. Rendering/Export APIs? No.

## 10. Fixtures Needed?
- compress-files, create-archive, compress-folder: Need input files/folders
- extract-files: Need an input archive file

## 11. License-Sensitive?
Trial limitations on archive size/count. Full API needs license.

## 12. Official Snippets?
- `CompressToTarBz2.cs` — Bzip2Archive + TarArchive pattern
- `CompressDirectory.cs` — Archive.CreateEntries(dirPath)

## 13. Classes/Methods?
- `Archive archive = new Archive()` — ZIP
- `archive.CreateEntry("filename.txt", filePath)` — add file
- `archive.Save(outputPath)` — save ZIP
- `archive.ExtractAll(destDir)` — extract
- `Archive(inputPath)` for reading existing archive

## 14. Plugins Sharing API Pattern?
compress-files, create-archive, compress-folder all use Archive class.
extract-files uses Archive(path).ExtractAll().

## 15. Plugins Needing Unique Mapping?
compress-folder: Uses CreateEntries(directoryPath) method.
extract-files: Uses Archive(path) constructor + ExtractAll.

## 16. Plugins with No Code?
extract-files: No direct match found. Pattern derivable from Archive docs.

## 17. Can Be Transformed Next Sprint?
- compress-files: YES
- create-archive: YES
- compress-folder: YES (needs test directory)
- extract-files: NEEDS_MANUAL_MAPPING (pattern clear but no direct file fetched)

## 18. Blockers?
Trial limitations may affect large archives.

## 19. Registry Strategy?
3 plugins READY_FOR_TRANSFORMATION; 1 (extract-files) NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. compress-files
2. create-archive

## Implementation Model
`LOAD_SAVE_OPTIONS` for compression path. `RECOGNITION_EXTRACTION_API` for extraction path.
