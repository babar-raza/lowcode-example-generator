# FormImporter Fixture Generation Proof

## Fixtures Tested
1. AcroForm PDF with text fields (programmatically generated)
2. Flat JSON: `{"name": "Test User"}`
3. Array JSON: `[{"fieldName": "name", "fieldValue": "Test User"}]`
4. Nested JSON: `{"Fields": [{"Name": "name", "Value": "Test User"}]}`

## Result
All 3 JSON formats produce the same NullReferenceException in `Form.ImportJson(Stream)`.
The crash is in Aspose internals, not in the fixture format.
