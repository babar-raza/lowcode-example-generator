# No-Stub Validator Rules
Date: 2026-05-30

A publication candidate FAILS if Program.cs contains:
- 'no suitable overload found'
- '// TODO'
- '// FIXME'
- '// placeholder'
- '// stub'

A publication candidate also FAILS if it:
- Has no LowCode main-class call
- Only prints to console without calling LowCode API
- Lacks example.manifest.json
- Lacks .csproj
- Lacks README.md
