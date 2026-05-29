# Lane Overlap Check

## Dependency Analysis

Lane 2 → Lane 3: Lane 2 modifies src/plugin_examples/generator/code_generator.py and pipeline/configs/families/*.yml. Lane 3 reads these to run clean generation. SEQUENTIAL: Lane 3 must run after Lane 2 completes.

Lane 3 → Lane 4: Lane 3 produces generated source in workspace/runs/clean-gen-*/generated/. Lane 4 reads these for build/run/validation. SEQUENTIAL.

Lane 4 → Lane 5: Lane 4 produces gate results. Lane 5 analyzes and repairs gate semantics. SEQUENTIAL.

Lane 2 → Lane 7: Lane 2 changes source files; Lane 7 runs full pytest which tests these files. SEQUENTIAL.

Lane 6 → Lane 8: Lane 6 produces package manifests. Lane 8 bundles them into ZIP. SEQUENTIAL.

All other lane pairs: INDEPENDENT (no shared output).

## Prohibited Overlaps
- No lane writes to another lane's output directory
- No lane modifies tracked files not in its scope
- Lanes 9-12 are independent of the core generation lanes

## Conflict Resolution
All sequential dependencies resolved by in-order execution. No circular dependencies detected.
