using System;
using System.IO;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

Console.WriteLine("=== Signature Harness ===");

// Step 1: Create self-signed PFX fixture
Console.WriteLine("Creating self-signed PFX...");
using var rsa = RSA.Create(2048);
var req = new CertificateRequest("cn=TestSign", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
var cert = req.CreateSelfSigned(DateTimeOffset.Now, DateTimeOffset.Now.AddYears(1));
var pfxBytes = cert.Export(X509ContentType.Pfx, "testpassword");
File.WriteAllBytes("test.pfx", pfxBytes);
Console.WriteLine("PFX created: test.pfx");

// Step 2: Create a PDF to sign
Console.WriteLine("Creating PDF fixture...");
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new Aspose.Pdf.Text.TextFragment("Document to sign"));
doc.Save("input.pdf");
Console.WriteLine("PDF fixture created: input.pdf");

// Step 3: Sign the PDF using Signature LowCode
Console.WriteLine("Signing PDF with Signature LowCode...");
try
{
    var signOptions = new SignOptions("test.pfx", "testpassword");
    signOptions.PageNumber = 1;
    signOptions.Reason = "Test Signature";
    signOptions.Contact = "test@example.com";
    signOptions.Location = "Test Location";
    signOptions.AddInput(new FileDataSource("input.pdf"));
    signOptions.AddOutput(new FileDataSource("output-signed.pdf"));
    var result = new Signature().Process(signOptions);
    Console.WriteLine($"Signature result: {result.ResultCollection.Count} items");
    Console.WriteLine($"Output file exists: {File.Exists("output-signed.pdf")}");
    Console.WriteLine("SIGNATURE_PASS");
}
catch (Exception ex)
{
    Console.WriteLine($"SIGNATURE_FAIL: {ex.GetType().Name}: {ex.Message}");
}
