using System;
using System.IO;
using Aspose.ThreeD;
using Aspose.ThreeD.Entities;

// Create a simple 3D scene with a box primitive
var scene = new Scene();
var box = new Box(1.0, 1.0, 1.0);
scene.RootNode.CreateChildNode("box", box);

// Save as WavefrontOBJ format
string outputPath = "output/model.obj";
Directory.CreateDirectory("output");
scene.Save(outputPath, FileFormat.WavefrontOBJ);
Console.WriteLine($"3D model converted and saved to {outputPath}");
