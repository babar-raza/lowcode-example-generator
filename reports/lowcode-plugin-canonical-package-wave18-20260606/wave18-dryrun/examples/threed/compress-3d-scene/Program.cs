// threed/compress-3d-scene — W18 canonical package proof
// Canonical URL: https://products.aspose.net/threed/compress-3d-scene/
// NuGet: Aspose.3D 24.12.0
// Pattern: Build Scene -> save as GLB binary (compact/compressed) vs ASCII FBX (verbose)
using System;
using System.IO;
using Aspose.ThreeD;
using Aspose.ThreeD.Entities;
using Aspose.ThreeD.Formats;

Directory.CreateDirectory("output");

// Build a scene with multiple geometry nodes
var scene = new Scene();
var box = new Box(2.0, 2.0, 2.0);
scene.RootNode.CreateChildNode("box-node", box);

var sphere = new Sphere(1.0);
var sphereNode = scene.RootNode.CreateChildNode("sphere-node", sphere);
sphereNode.Transform.Translation = new Aspose.ThreeD.Utilities.Vector3(3, 0, 0);

// Save as glTF binary (.glb) — compact binary format (smaller, compressed)
string glbPath = "output/scene-compressed.glb";
var gltfOpts = new GltfSaveOptions(FileContentType.Binary);
scene.Save(glbPath, gltfOpts);
long glbSize = new FileInfo(glbPath).Length;
Console.WriteLine($"Compressed GLB saved: {glbPath} ({glbSize} bytes)");

// Save as ASCII FBX — verbose text format (larger, uncompressed) for size comparison
string fbxPath = "output/scene-uncompressed.fbx";
scene.Save(fbxPath, new FbxSaveOptions(FileContentType.ASCII));
long fbxSize = new FileInfo(fbxPath).Length;
Console.WriteLine($"Uncompressed FBX (ASCII) saved: {fbxPath} ({fbxSize} bytes)");

// Compression summary
double ratio = fbxSize > 0 ? (double)glbSize / fbxSize : 0;
string summary = $"Compressed GLB binary:    {glbSize,8} bytes\nUncompressed FBX ASCII:   {fbxSize,8} bytes\nSize ratio (GLB/FBX):      {ratio:P1}";
File.WriteAllText("output/compression-result.txt", summary);
Console.WriteLine("Compression complete.");
Console.WriteLine(summary);
