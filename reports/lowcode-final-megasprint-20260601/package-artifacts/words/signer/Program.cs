using System;
using System.IO;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using Aspose.Words.DigitalSignatures;
using Aspose.Words.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: words-signer");

            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");
            string outputPath = "output.docx";

            // Generate a self-signed test certificate for demonstration
            string pfxPath = "test-cert.pfx";
            const string pfxPassword = "test-password";
            using (var rsa = RSA.Create(2048))
            {
                var request = new CertificateRequest(
                    "CN=Aspose Test Signer, O=Test, C=US",
                    rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                var cert = request.CreateSelfSigned(
                    DateTimeOffset.Now.AddDays(-1),
                    DateTimeOffset.Now.AddYears(1));
                File.WriteAllBytes(pfxPath, cert.Export(X509ContentType.Pfx, pfxPassword));
            }

            // Use SignerContext from Aspose.Words.LowCode to configure signing
            var signerCtx = new SignerContext();
            signerCtx.CertificateHolder = CertificateHolder.Create(pfxPath, pfxPassword);
            signerCtx.SignOptions = new SignOptions { SignTime = new DateTime(2026, 5, 31) };

            // Sign the document using DigitalSignatureUtil
            DigitalSignatureUtil.Sign(inputPath, outputPath,
                signerCtx.CertificateHolder, signerCtx.SignOptions);

            var signatures = DigitalSignatureUtil.LoadSignatures(outputPath);
            Console.WriteLine(File.Exists(outputPath)
                ? $"Signing succeeded: {outputPath}, Signatures: {signatures.Count}"
                : "Signing failed: output file not found.");

            Console.WriteLine("Done.");
        }
    }
}
