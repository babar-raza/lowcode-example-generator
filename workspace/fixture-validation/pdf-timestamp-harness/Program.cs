using System;
using System.IO;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

Console.WriteLine("=== Timestamp Harness ===");

// Create a PDF to timestamp
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new Aspose.Pdf.Text.TextFragment("Document to timestamp"));
doc.Save("input.pdf");
Console.WriteLine("PDF created: input.pdf");

// Test 1: No-param TimestampOptions (no TSA)
Console.WriteLine("\n--- Test 1: TimestampOptions() no-param ---");
try
{
    var tsOpts = new TimestampOptions();
    tsOpts.AddInput(new FileDataSource("input.pdf"));
    tsOpts.AddOutput(new FileDataSource("output-ts-noparam.pdf"));
    Console.WriteLine($"  ServerUrl: '{tsOpts.ServerUrl ?? "null"}'");
    var result = new Timestamp().Process(tsOpts);
    Console.WriteLine($"  result.Count: {result.ResultCollection.Count}");
    Console.WriteLine($"  output exists: {File.Exists("output-ts-noparam.pdf")}");
    Console.WriteLine("  TIMESTAMP_NOPARAM_PASS");
}
catch (Exception ex)
{
    Console.WriteLine($"  TIMESTAMP_NOPARAM_FAIL: {ex.GetType().Name}: {ex.Message}");
}

// Test 2: TimestampOptions with PFX (local signing, no external TSA)
Console.WriteLine("\n--- Test 2: TimestampOptions(pfx, password) ---");
try
{
    using var rsa = RSA.Create(2048);
    var req = new CertificateRequest("cn=TestTimestamp", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
    var cert = req.CreateSelfSigned(DateTimeOffset.Now, DateTimeOffset.Now.AddYears(1));
    var pfxBytes = cert.Export(X509ContentType.Pfx, "testpassword");
    File.WriteAllBytes("test-ts.pfx", pfxBytes);

    var tsOpts2 = new TimestampOptions("test-ts.pfx", "testpassword");
    tsOpts2.AddInput(new FileDataSource("input.pdf"));
    tsOpts2.AddOutput(new FileDataSource("output-ts-pfx.pdf"));
    var result2 = new Timestamp().Process(tsOpts2);
    Console.WriteLine($"  result.Count: {result2.ResultCollection.Count}");
    Console.WriteLine($"  output exists: {File.Exists("output-ts-pfx.pdf")}");
    Console.WriteLine("  TIMESTAMP_PFX_PASS");
}
catch (Exception ex)
{
    Console.WriteLine($"  TIMESTAMP_PFX_FAIL: {ex.GetType().Name}: {ex.Message}");
}
