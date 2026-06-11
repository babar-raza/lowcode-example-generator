"""Prompt sanitization for LLM inputs and generated code safety checks.

RISK-07: Prevents injection attacks via compiler/runtime error output.
RISK-08: Redacts secrets and sensitive paths from prompt text.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# RISK-07  sanitize_llm_input
# ---------------------------------------------------------------------------

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_INJECTION_LINE_RE = re.compile(
    r"^\s*(System|User|Assistant|IGNORE|Forget)\s*:", re.IGNORECASE
)

_MAX_SANITIZED_LEN = 800


def sanitize_llm_input(text: str) -> str:
    """Strip dangerous patterns from compiler/runtime output before LLM prompt use.

    - Removes ANSI escape codes
    - Removes control characters (except newline and tab)
    - Removes lines that look like prompt-injection attempts
    - Truncates to 800 characters
    """
    if not text:
        return ""
    text = _ANSI_RE.sub("", text)
    text = _CONTROL_RE.sub("", text)
    lines = text.splitlines(keepends=True)
    cleaned = [ln for ln in lines if not _INJECTION_LINE_RE.match(ln)]
    result = "".join(cleaned)
    return result[:_MAX_SANITIZED_LEN]


# ---------------------------------------------------------------------------
# RISK-07  check_generated_code_safety
# ---------------------------------------------------------------------------

_DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bHttpClient\b"), "HttpClient usage — network access"),
    (re.compile(r"\bWebClient\b"), "WebClient usage — network access"),
    (re.compile(r"\bWebRequest\b"), "WebRequest usage — network access"),
    (re.compile(r"\bProcess\.Start\b"), "Process.Start — arbitrary process execution"),
    (re.compile(r"\bAssembly\.Load\b"), "Assembly.Load — dynamic assembly loading"),
    (re.compile(r"\bActivator\.CreateInstance\b"), "Activator.CreateInstance — dynamic instantiation"),
    (re.compile(r"\bType\.GetType\b"), "Type.GetType — reflection-based type resolution"),
    (re.compile(r"\bAppDomain\b"), "AppDomain usage — cross-domain execution"),
    (re.compile(r"\beval\s*\("), "eval() — dynamic code evaluation"),
    (re.compile(r"\bdynamic\b"), "dynamic keyword — bypasses compile-time type safety"),
]


def check_generated_code_safety(code: str) -> list[str]:
    """Check generated C# code for dangerous operations.

    Returns a list of violation descriptions. An empty list means the code
    is considered safe.
    """
    if not code:
        return []
    violations: list[str] = []
    for pattern, description in _DANGEROUS_PATTERNS:
        if pattern.search(code):
            violations.append(description)
    return violations


# ---------------------------------------------------------------------------
# RISK-08  scrub_secrets
# ---------------------------------------------------------------------------

_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # OpenAI-style API keys
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "[REDACTED-API-KEY]"),
    # GitHub personal access tokens
    (re.compile(r"\bghp_[A-Za-z0-9]{36,}\b"), "[REDACTED-GHP-TOKEN]"),
    # GitHub OAuth tokens
    (re.compile(r"\bgho_[A-Za-z0-9]{36,}\b"), "[REDACTED-GHO-TOKEN]"),
    # Bearer tokens in header-like context
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}"), "Bearer [REDACTED-TOKEN]"),
    # Absolute Windows user paths
    (re.compile(r"[A-Z]:\\Users\\[^\s\\\"']+(?:\\[^\s\\\"']+)*"), "[REDACTED-PATH]"),
    # Generic long hex/base64 secrets (40+ chars, likely tokens)
    (re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b"), "[REDACTED-SECRET]"),
]


def scrub_secrets(text: str) -> str:
    """Redact API keys, tokens, and sensitive paths from prompt text (RISK-08).

    Applies pattern-based redaction for known secret formats. Returns
    the scrubbed text.
    """
    if not text:
        return ""
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text
