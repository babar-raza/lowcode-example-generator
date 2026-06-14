# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.29.x  | Yes       |
| 0.28.x  | Yes       |
| < 0.28  | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do not open a public issue.** Instead, send an email to the project maintainers with:

1. A description of the vulnerability
2. Steps to reproduce the issue
3. Any relevant logs, screenshots, or proof-of-concept code
4. Your assessment of severity (LOW / MEDIUM / HIGH / CRITICAL)

### Response Timeline

- **Acknowledgement**: within 72 hours of report
- **Initial assessment**: within 7 days
- **Fix for HIGH/CRITICAL**: within 30 days
- **Fix for MEDIUM/LOW**: next scheduled release

## Scope

The following are considered in-scope security issues:

- **Template injection**: malicious input that causes generated C# code to execute unintended operations
- **Credential leakage**: secrets, tokens, or API keys exposed in logs, artifacts, or generated output
- **LLM output safety**: prompt injection or adversarial input that causes the LLM router to produce unsafe code
- **Arbitrary code execution**: any path that allows untrusted input to execute system commands
- **Dependency vulnerabilities**: known CVEs in project dependencies

The following are out of scope:

- Issues in upstream Aspose NuGet packages (report to Aspose directly)
- Issues in the .NET SDK or runtime
- Denial of service against CI/CD pipelines (rate limiting is an infrastructure concern)

## Existing Security Tooling

This project uses automated security scanning as part of its CI pipeline:

- **Bandit SAST**: static analysis for Python security issues, configured in `pyproject.toml` and enforced as a blocking CI gate
- **pip-audit**: advisory dependency vulnerability scanning in CI
- **Pre-commit hooks**: bandit runs on every commit via `.pre-commit-config.yaml`
- **License policy**: dependency licenses are validated against an allowlist (EHV-08 validator)
- **Gate isolation**: AI/LLM modules are prohibited from importing into gate modules (ADR-002, RISK-10)

## Disclosure Policy

We follow coordinated vulnerability disclosure. After a fix is released, we will:

1. Credit the reporter (unless anonymity is requested)
2. Document the fix in CHANGELOG.md
3. Update the affected version table above
