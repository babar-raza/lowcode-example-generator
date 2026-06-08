# Family Manual Analysis: threed

## Date: 2026-06-04
## Evidence: GitHub repo aspose-3d/Aspose.3D-for-.NET, code: SceneHierarchyTree.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Scene class with Load/Save.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Scene` — main 3D scene container
- `FileFormat` — format enum (FBX, OBJ, STL, GLTF, etc.)

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `scene.Save(outputPath, FileFormat.FBX7400ASCII)`.
## 7. Document Object Model Workflow? Yes. Scene has Node hierarchy, geometry, materials.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. 3D scene export to various formats.

## 10. Fixtures Needed?
Yes. Both plugins need input 3D model files (FBX, OBJ, STL etc.).

## 11. License-Sensitive?
Trial watermark/limitations on output. Prior sprint: PROBE_BLOCKED_LICENSE.

## 12. Official Snippets?
- `SceneHierarchyTree.cs` — Scene hierarchy navigation (not a direct conversion example)

## 13. Classes/Methods?
- `Scene scene = new Scene(inputPath);`
- `scene.Save(outputPath, FileFormat.FBX7400ASCII);`
- `Scene scene = Scene.FromFile(inputPath);` (alternate)
- `scene.RootNode` — traverse node hierarchy

## 14. Plugins Sharing API Pattern?
convert-3d-model: Scene.Load + Save with format
compress-3d-scene: May use A3DW (Aspose 3D Web) format or compact representation

## 15. Plugins Needing Unique Mapping?
compress-3d-scene: Different output format (possibly A3DW or compressed FBX)

## 16. Plugins with No Code?
Both matched but to same file (SceneHierarchyTree, not ideal conversion example).

## 17. Can Be Transformed Next Sprint?
- convert-3d-model: YES with 3D fixture file, but ENVIRONMENT_DEPENDENT (license watermark)
- compress-3d-scene: NEEDS_MANUAL_MAPPING

## 18. Blockers?
License watermark on trial. 3D fixture file needed.

## 19. Registry Strategy?
Both ENVIRONMENT_DEPENDENT. convert-3d-model READY_FOR_TRANSFORMATION with caveat.

## 20. First Transformation Candidates?
1. convert-3d-model

## Implementation Model
`LOAD_SAVE_OPTIONS` — Scene.Load() + Save(format).
