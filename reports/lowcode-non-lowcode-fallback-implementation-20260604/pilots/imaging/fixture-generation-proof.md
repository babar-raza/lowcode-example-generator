# Imaging TIER-1 Fixture Generation Proof

Fixture: 1x1 red pixel PNG
Generator: reports/.../prototypes/imaging/probe/fixture_gen.py
Method: Python bytes + zlib only; no Pillow; no binary committed
Output size: 69 bytes (programmatic PNG header + IHDR + IDAT + IEND)

## SHA-256 Verification

The fixture is generated at probe runtime, not committed to git.
fixture_gen.py creates the file deterministically each run.
Provenance: TIER-1 (programmatic — highest quality)
