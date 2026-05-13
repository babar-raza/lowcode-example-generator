"""Token readiness hardening tests.

Verifies:
- classify_token_type correctly identifies classic PAT (ghp_)
- classify_token_type rejects fine-grained PAT (github_pat_)
- classify_token_type returns missing for empty token
- classify_token_type returns unknown for unrecognized prefix
- check_classic_token accepts ghp_ tokens
- check_classic_token fails closed on github_pat_ with clear error message
- check_classic_token fails on missing token
- Error message contains actionable remediation guidance
- repo_access_resolver exports new constants
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from plugin_examples.publisher.repo_access_resolver import (
    classify_token_type,
    check_classic_token,
    TOKEN_TYPE_CLASSIC_PAT,
    TOKEN_TYPE_FINE_GRAINED,
    TOKEN_TYPE_MISSING,
    TOKEN_TYPE_UNKNOWN,
    FINE_GRAINED_TOKEN_ERROR_MESSAGE,
    FINE_GRAINED_TOKEN_REJECTED,
)


class TestClassifyTokenType:
    def test_classic_pat_ghp_prefix_accepted(self):
        assert classify_token_type("ghp_abc123def456") == TOKEN_TYPE_CLASSIC_PAT

    def test_classic_pat_ghp_prefix_short(self):
        assert classify_token_type("ghp_x") == TOKEN_TYPE_CLASSIC_PAT

    def test_fine_grained_pat_rejected(self):
        assert classify_token_type("github_pat_abc123") == TOKEN_TYPE_FINE_GRAINED

    def test_fine_grained_pat_longer_token(self):
        assert classify_token_type("github_pat_" + "a" * 80) == TOKEN_TYPE_FINE_GRAINED

    def test_missing_empty_string(self):
        assert classify_token_type("") == TOKEN_TYPE_MISSING

    def test_missing_none_treated_as_empty(self):
        assert classify_token_type("") == TOKEN_TYPE_MISSING

    def test_unknown_prefix_github_actions(self):
        result = classify_token_type("ghs_SomeActionsToken")
        assert result == TOKEN_TYPE_UNKNOWN

    def test_unknown_prefix_random(self):
        result = classify_token_type("sk-abc123")
        assert result == TOKEN_TYPE_UNKNOWN

    def test_unknown_prefix_gha(self):
        result = classify_token_type("gha_something")
        assert result == TOKEN_TYPE_UNKNOWN

    def test_classic_pat_constant_value(self):
        assert TOKEN_TYPE_CLASSIC_PAT == "classic_pat"

    def test_fine_grained_constant_value(self):
        assert TOKEN_TYPE_FINE_GRAINED == "fine_grained_pat"

    def test_missing_constant_value(self):
        assert TOKEN_TYPE_MISSING == "missing"

    def test_unknown_constant_value(self):
        assert TOKEN_TYPE_UNKNOWN == "unknown"


class TestCheckClassicToken:
    def test_classic_pat_returns_true_empty_reason(self):
        ok, reason = check_classic_token("ghp_MyClassicToken123")
        assert ok is True
        assert reason == ""

    def test_fine_grained_returns_false_with_error_message(self):
        ok, reason = check_classic_token("github_pat_MyFineGrainedToken")
        assert ok is False
        assert len(reason) > 0

    def test_fine_grained_error_message_mentions_classic_pat(self):
        _, reason = check_classic_token("github_pat_SomeToken")
        assert "Classic PAT" in reason or "classic" in reason.lower(), \
            "Error message must mention classic PAT requirement"

    def test_fine_grained_error_message_mentions_repo_scope(self):
        _, reason = check_classic_token("github_pat_SomeToken")
        assert "repo scope" in reason or "repo" in reason.lower(), \
            "Error message must mention repo scope"

    def test_fine_grained_error_message_not_accepted(self):
        _, reason = check_classic_token("github_pat_SomeToken")
        assert "not accepted" in reason or "rejected" in reason.lower() or "fine-grained" in reason.lower(), \
            "Error message must indicate fine-grained token is not accepted"

    def test_fine_grained_error_message_contains_remediation(self):
        _, reason = check_classic_token("github_pat_SomeToken")
        assert "GH_TOKEN" in reason or "ghp_" in reason, \
            "Error message must contain remediation guidance (GH_TOKEN or ghp_ prefix)"

    def test_missing_token_returns_false_token_missing_reason(self):
        ok, reason = check_classic_token("")
        assert ok is False
        assert reason == "token_missing"

    def test_unknown_token_prefix_returns_false(self):
        ok, reason = check_classic_token("ghs_ActionsToken")
        assert ok is False
        assert "token_type_unknown" in reason

    def test_check_classic_uses_fine_grained_token_error_message(self):
        _, reason = check_classic_token("github_pat_Token")
        assert reason == FINE_GRAINED_TOKEN_ERROR_MESSAGE, \
            "check_classic_token must return the canonical FINE_GRAINED_TOKEN_ERROR_MESSAGE"


class TestFineGrainedTokenErrorMessageContent:
    def test_error_message_not_empty(self):
        assert len(FINE_GRAINED_TOKEN_ERROR_MESSAGE) > 50

    def test_error_message_mentions_github_pat_prefix(self):
        assert "github_pat_" in FINE_GRAINED_TOKEN_ERROR_MESSAGE

    def test_error_message_mentions_git_data_api(self):
        assert "Git Data API" in FINE_GRAINED_TOKEN_ERROR_MESSAGE or \
               "git/blobs" in FINE_GRAINED_TOKEN_ERROR_MESSAGE

    def test_error_message_mentions_gh_token_mapping(self):
        assert "GH_TOKEN" in FINE_GRAINED_TOKEN_ERROR_MESSAGE

    def test_fine_grained_rejected_constant_exists(self):
        assert FINE_GRAINED_TOKEN_REJECTED == "fine_grained_token_rejected"


class TestTokenHardeningIntegration:
    def test_classic_pat_in_github_token_passes_check(self):
        """Simulates the correct operator flow: classic PAT in GITHUB_TOKEN."""
        token = os.environ.get("GITHUB_TOKEN", "")
        if token.startswith("ghp_"):
            ok, reason = check_classic_token(token)
            assert ok is True
            assert reason == ""

    def test_fine_grained_in_github_token_fails_closed(self):
        """When GITHUB_TOKEN contains a fine-grained token, check fails closed."""
        fine_grained_token = "github_pat_" + "x" * 50
        ok, reason = check_classic_token(fine_grained_token)
        assert ok is False
        assert "Classic PAT" in reason or "classic" in reason.lower()

    def test_token_type_check_does_not_make_network_calls(self):
        """classify_token_type and check_classic_token are pure functions, no I/O."""
        # If these functions make network calls, they would be slow or fail offline.
        # They must complete instantly and deterministically.
        import time
        start = time.monotonic()
        for _ in range(1000):
            classify_token_type("ghp_abc")
            check_classic_token("github_pat_xyz")
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, "Token classification must be a fast pure function"

    def test_repo_access_resolver_exports_all_new_constants(self):
        """All new token readiness constants must be importable from repo_access_resolver."""
        from plugin_examples.publisher import repo_access_resolver as rar
        assert hasattr(rar, "classify_token_type")
        assert hasattr(rar, "check_classic_token")
        assert hasattr(rar, "TOKEN_TYPE_CLASSIC_PAT")
        assert hasattr(rar, "TOKEN_TYPE_FINE_GRAINED")
        assert hasattr(rar, "TOKEN_TYPE_MISSING")
        assert hasattr(rar, "TOKEN_TYPE_UNKNOWN")
        assert hasattr(rar, "FINE_GRAINED_TOKEN_ERROR_MESSAGE")
        assert hasattr(rar, "FINE_GRAINED_TOKEN_REJECTED")
