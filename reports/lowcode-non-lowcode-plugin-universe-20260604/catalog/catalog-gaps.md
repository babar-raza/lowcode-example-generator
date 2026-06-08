# Catalog Gaps Report — Plugin Universe 20260604

Generated: 2026-06-04T00:00:00Z

## Summary

| metric | value |
|--------|-------|
| Families in KNOWN_PLUGINS | 18 |
| Total plugins cataloged | 65 |
| Families discovered from web root | 0 (web root parse returned 0 family slugs) |
| Missing from package-aliases.json | 0 |

## Web Discovery Result

The `products.aspose.net` root page returned 0 family slugs from the regex pattern
`href="/([a-z0-9-]+)/net[/"'>]`. This is expected in offline/blocked environments;
all 18 families are covered by the `KNOWN_PLUGINS` static table.

## Families NOT in Catalog (gaps)

The following families exist in `package-aliases.json` but have zero plugins cataloged
(no known plugin slugs for these families):

| family | package_id | status |
|--------|-----------|--------|
| epub | Aspose.HTML | verify — may share HTML namespace |
| medical | Aspose.Medical | verify — new package; plugin URLs TBD |

## Plugin Coverage by Family

| family | plugins | verbs | formats (sample) |
|--------|---------|-------|------------------|
| barcode | 5 | generate, recognize, read, scan | PNG, JPG, BMP, GIF, TIFF, SVG |
| imaging | 8 | convert, resize, compress, crop, rotate, watermark, merge, filter | PNG, JPG, BMP, GIF, TIFF, WEBP, PSD, SVG |
| zip | 4 | compress, extract, create, archive | ZIP, RAR, 7Z, TAR, GZ |
| html | 6 | convert, merge | HTML, PDF, DOCX, XPS, MD |
| tasks | 5 | convert, read, parse | MPP, PDF, XLSX, HTML, PNG, JPG, XML |
| cad | 5 | convert | DWG, DXF, PDF, PNG, JPG |
| ocr | 3 | recognize, extract, scan | PNG, JPG, BMP, TIFF, PDF |
| psd | 4 | convert, edit | PSD, PDF, PNG, JPG |
| svg | 4 | convert, merge | SVG, PDF, PNG, JPG |
| omr | 2 | recognize, generate | PNG, JPG, BMP, PDF |
| gis | 2 | convert, read, parse | SHP, GeoJSON, KML, GPX |
| page | 3 | convert | XPS, EPS, PS, PDF |
| tex | 3 | convert | TEX, PDF, SVG |
| note | 3 | convert | ONE, PDF, DOCX, PNG, JPG |
| drawing | 2 | convert, create | EMF, WMF, SVG, PNG, JPG |
| font | 2 | convert, render | TTF, WOFF, EOT, CFF, PNG, JPG |
| finance | 2 | convert, validate, parse, read | XBRL, JSON, XLSX, iXBRL |
| threed | 2 | convert, compress | FBX, OBJ, STL, 3DS, GLTF |

## Recommendations

1. **epub** — treat as `Aspose.HTML` alias; use HTML family plugin URLs
2. **medical** — defer to WAVE-4 pending package availability verification
3. **web root parsing** — consider sitemap.xml-based discovery as fallback
4. **Priority for reflection wave** — barcode, imaging, zip, html, tasks, cad, ocr (Wave 1)
