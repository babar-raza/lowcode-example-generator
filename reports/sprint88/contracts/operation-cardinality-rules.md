Sprint 88 — Operation Cardinality Rules
=========================================
Date: 2026-05-25

## Rules by Family

### Cells (9 examples)
| Example | Operation | Cardinality |
|---------|-----------|-------------|
| html-converter | converter | 1-to-1 |
| image-converter | converter | 1-to-1 |
| json-converter | converter | 1-to-1 |
| pdf-converter | converter | 1-to-1 |
| spreadsheet-converter | converter | 1-to-1 |
| spreadsheet-locker | locker | 1-to-1 |
| spreadsheet-merger | merger | N-to-1 |
| spreadsheet-splitter | splitter | 1-to-N |
| text-converter | converter | 1-to-1 |

### Words (8 examples)
| Example | Operation | Cardinality |
|---------|-----------|-------------|
| comparer | editor | 1-to-1 |
| converter | converter | 1-to-1 |
| mail-merger | merger | N-to-1 |
| merger | merger | N-to-1 |
| replacer | editor | 1-to-1 |
| report-builder | renderer | 1-to-1 |
| splitter | splitter | 1-to-N |
| watermarker | editor | 1-to-1 |

### PDF (19 examples)
| Example | Operation | Cardinality |
|---------|-----------|-------------|
| doc-converter | converter | 1-to-1 |
| form-editor | editor | 1-to-1 |
| form-exporter | extractor | 1-to-stdout |
| form-flattener | editor | 1-to-1 |
| html | converter | 1-to-1 |
| image-extractor | extractor | 1-to-files |
| jpeg | converter | 1-to-1 |
| merger | merger | N-to-1 |
| optimizer | compressor | 1-to-1 |
| pdfa-converter | converter | 1-to-1 |
| png | converter | 1-to-1 |
| security | locker | 1-to-1 |
| signature | editor | 1-to-1 |
| splitter | splitter | 1-to-N |
| table-generator | renderer | 1-to-1 |
| text-extractor | extractor | 1-to-stdout |
| tiff | converter | 1-to-1 |
| toc-generator | editor | 1-to-1 |
| xls-converter | converter | 1-to-1 |

### Diagram (2 examples)
| Example | Operation | Cardinality |
|---------|-----------|-------------|
| diagram-converter | converter | 1-to-1 |
| pdf-converter | converter | 1-to-1 |

### Email (1 example)
| Example | Operation | Cardinality |
|---------|-----------|-------------|
| converter | converter | 1-to-1 |

### Slides (3 examples)
| Example | Operation | Cardinality |
|---------|-----------|-------------|
| compress | compressor | 1-to-1 |
| convert | converter | 1-to-1 |
| merger | merger | N-to-1 |
