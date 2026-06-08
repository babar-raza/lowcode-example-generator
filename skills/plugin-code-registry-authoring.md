# Skill: Plugin-Code Registry Authoring

## Purpose
Create or update a plugin-code registry YAML entry from page, code, and manual analysis evidence.

## Inputs
- family_slug
- plugin_slug
- plugin_url (canonical URL)
- page_hash (from crawl)
- harvest_result (from code harvest)
- symbol_result (from code harvest)
- family_analysis (from manual analysis)

## Outputs
- pipeline/plugin-code-registry/family/{family}.yaml (entry appended or updated)
- pipeline/plugin-code-registry/registry-index.json (updated)

## Prerequisites
- Plugin page URL confirmed (real products.aspose.net URL)
- Code harvest run (may result in NO_CODE_FOUND — that's OK)
- Family manual analysis exists

## Step-by-Step Method

1. Collect evidence:
   - page_url + page_hash from crawl/plugin-page-hash-ledger.json
   - code_hash, raw_url, filename from code-harvest/source-link-inventory.json
   - namespaces, classes, methods from code-harvest/code-symbol-inventory.json
   - implementation_model, next_action from manual analysis

2. Determine registry_status:
   - If BLOCKED_LICENSE: status = BLOCKED_LICENSE
   - If no code found: status = NEEDS_MANUAL_MAPPING
   - If wrong/caveat code fetched: status = NEEDS_MANUAL_MAPPING
   - If good code fetched: status = CODE_HARVESTED
   - After DllReflector confirms classes exist: status = REFLECTION_CONFIRMED
   - After probe runs successfully: status = PROBE_CONFIRMED
   - After all evidence + probe: status = READY_FOR_TRANSFORMATION

3. Write YAML entry with required fields:
   - plugin_slug, plugin_url, page_hash
   - registry_status
   - blocker_type (null if no blocker)
   - implementation_model
   - code_hashes (empty list if no code)
   - namespaces_used, classes_used (from symbols)
   - github_links (raw_url)
   - next_action (specific, actionable)
   - evidence_paths (minimum 3: inventory, harvest manifest, family analysis)
   - history (date + status + analyst_notes)

4. Validate entry against invariants:
   - Has evidence_paths?
   - Has history?
   - Has next_action?
   - If READY_FOR_TRANSFORMATION: has code_hashes?
   - If WEBSITE_PATTERN_UNVERIFIED: NOT READY_FOR_TRANSFORMATION?

5. Update registry-index.json with new entry summary

## Checks
- [ ] All required fields present
- [ ] history has at least 1 record
- [ ] evidence_paths has at least 1 real path
- [ ] next_action is actionable (not "TBD")
- [ ] blocker_type is null or valid enum value
- [ ] code_hashes present if READY_FOR_TRANSFORMATION

## Failure Modes
- Missing evidence: Downgrade status (e.g., PAGE_DISCOVERED instead of CODE_HARVESTED)
- Schema violation: Repair before writing
- Duplicate entry: Update existing, add to history

## Evidence Requirements
- At minimum: plugin_url + page_hash + family analysis reference
- Preferred: + code_hash + code file path

## Example Entry
See: pipeline/plugin-code-registry/family/barcode.yaml

## Stop Rules
- NEVER create a READY_FOR_TRANSFORMATION entry without code_hashes
- NEVER use family probe as plugin-level evidence
- NEVER mark WEBSITE_PATTERN_UNVERIFIED as ready

## Continue Rules
- NEEDS_MANUAL_MAPPING entries are valid registry entries
- No evidence = PAGE_DISCOVERED (not failure)
