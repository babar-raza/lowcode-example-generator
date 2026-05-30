using System;
using System.IO;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

// Create self-signed PFX fixture (no TSA/CA server required)
using var rsa = RSA.Create(2048);
var req = new CertificateRequest("cn=TestSign", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
var cert = req.CreateSelfSigned(DateTimeOffset.Now, DateTimeOffset.Now.AddYears(1));
var pfxBytes = cert.Export(X509ContentType.Pfx, "testpassword");
File.WriteAllBytes("test.pfx", pfxBytes);

// Create PDF input fixture
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new TextFragment("Document for digital signing"));
doc.Save("input.pdf");

// Apply digital signature using Signature LowCode plugin
var signOptions = new SignOptions("test.pfx", "testpassword");
signOptions.PageNumber = 1;
signOptions.Reason = "Authorized Signature";
signOptions.Contact = "signatory@example.com";
signOptions.Location = "Document Processing";
signOptions.AddInput(new FileDataSource("input.pdf"));
signOptions.AddOutput(new FileDataSource("output.pdf"));
var result = new Signature().Process(signOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "PDF signed successfully." : "No output produced.");
