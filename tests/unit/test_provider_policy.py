"""Unit tests for LLM provider policy enforcement."""

from __future__ import annotations

import pytest

from plugin_examples.llm_router.provider_policy import (
    APPROVED_PROVIDERS,
    FORBIDDEN_PIPELINE_MODELS,
    UNAPPROVED_PROVIDERS,
    classify_documentation_hit,
    classify_llm_hit,
    classify_provider_hit,
    filter_to_approved,
    get_policy_violations,
    is_direct_openai_construction,
    is_forbidden_model,
    validate_model_for_provider,
    validate_provider_family,
)


class TestApprovedProviderConstants:
    def test_approved_contains_professionalize(self):
        assert "llm_professionalize" in APPROVED_PROVIDERS

    def test_approved_contains_ollama(self):
        assert "ollama" in APPROVED_PROVIDERS

    def test_approved_is_frozen(self):
        assert isinstance(APPROVED_PROVIDERS, frozenset)

    def test_unapproved_contains_gpt_oss(self):
        assert "gpt_oss" in UNAPPROVED_PROVIDERS

    def test_unapproved_contains_openai(self):
        assert "openai" in UNAPPROVED_PROVIDERS

    def test_unapproved_contains_azure_openai(self):
        assert "azure_openai" in UNAPPROVED_PROVIDERS

    def test_no_overlap_between_approved_and_unapproved(self):
        assert APPROVED_PROVIDERS.isdisjoint(UNAPPROVED_PROVIDERS)

    def test_forbidden_models_contains_gpt4o_mini(self):
        assert "gpt-4o-mini" in FORBIDDEN_PIPELINE_MODELS


class TestGetPolicyViolations:
    def test_no_violations_for_approved(self):
        assert get_policy_violations(["llm_professionalize", "ollama"]) == []

    def test_violations_for_unapproved(self):
        result = get_policy_violations(["openai", "llm_professionalize"])
        assert result == ["openai"]

    def test_violations_for_multiple_unapproved(self):
        result = get_policy_violations(["gpt_oss", "azure_openai"])
        assert len(result) == 2

    def test_empty_input(self):
        assert get_policy_violations([]) == []

    def test_unknown_provider_not_violation(self):
        assert get_policy_violations(["some_random_provider"]) == []


class TestFilterToApproved:
    def test_filters_correctly(self):
        result = filter_to_approved(["openai", "llm_professionalize", "ollama"])
        assert result == ["llm_professionalize", "ollama"]

    def test_empty_when_all_unapproved(self):
        assert filter_to_approved(["openai", "gpt_oss"]) == []

    def test_preserves_order(self):
        result = filter_to_approved(["ollama", "llm_professionalize"])
        assert result == ["ollama", "llm_professionalize"]


class TestClassifyProviderHit:
    def test_approved_provider(self):
        result = classify_provider_hit("router.py", "llm_professionalize", "config")
        assert result["classification"] == "approved_llm_provider_config"
        assert result["approved"] is True

    def test_unapproved_provider(self):
        result = classify_provider_hit("bad.py", "openai", "import")
        assert result["classification"] == "violation_unapproved_provider"
        assert result["approved"] is False

    def test_unknown_provider(self):
        result = classify_provider_hit("file.py", "custom_llm", "ref")
        assert result["classification"] == "unknown"
        assert result["approved"] is False


class TestIsForbiddenModel:
    def test_gpt4o_mini_forbidden(self):
        assert is_forbidden_model("gpt-4o-mini") is True

    def test_other_model_not_forbidden(self):
        assert is_forbidden_model("gpt-4o") is False

    def test_gpt_oss_as_model_not_forbidden(self):
        assert is_forbidden_model("gpt_oss") is False


class TestClassifyDocumentationHit:
    def test_xml_file_classified_as_docs(self):
        result = classify_documentation_hit("some text", "path/to/api.xml")
        assert result["classification"] == "extracted_nuget_documentation"
        assert result["is_pipeline_call"] is False

    def test_nuget_path_classified_as_docs(self):
        result = classify_documentation_hit("text", "path/nuget/extracted/file.txt")
        assert result["classification"] == "extracted_nuget_documentation"

    def test_non_doc_classified_as_ambiguous(self):
        result = classify_documentation_hit("text", "src/router.py")
        assert result["classification"] == "ambiguous_needs_fix"


class TestIsDirectOpenaiConstruction:
    def test_approved_path_allowed(self):
        assert is_direct_openai_construction(
            "client = OpenAI(api_key=k)",
            "src/plugin_examples/llm_router/providers/professionalize.py",
        ) is False

    def test_unapproved_path_forbidden(self):
        assert is_direct_openai_construction(
            "client = OpenAI(api_key=k)",
            "src/plugin_examples/generator/code_generator.py",
        ) is True

    def test_no_openai_call(self):
        assert is_direct_openai_construction(
            "import openai",
            "src/any.py",
        ) is False


class TestValidateProviderFamily:
    def test_approved_returns_empty(self):
        assert validate_provider_family("llm_professionalize") == []

    def test_unapproved_returns_violations(self):
        violations = validate_provider_family("openai")
        assert len(violations) == 2  # not approved + explicitly forbidden

    def test_unknown_returns_one_violation(self):
        violations = validate_provider_family("custom_llm")
        assert len(violations) == 1  # not approved (but not explicitly forbidden)


class TestValidateModelForProvider:
    def test_allowed_model(self):
        assert validate_model_for_provider("llm_professionalize", "gpt-4o") == []

    def test_forbidden_model(self):
        violations = validate_model_for_provider("ollama", "gpt-4o-mini")
        assert len(violations) == 1
        assert "forbidden" in violations[0].lower()

    def test_gpt_oss_as_model_under_ollama_allowed(self):
        assert validate_model_for_provider("ollama", "gpt_oss") == []


class TestClassifyLlmHit:
    def test_xml_doc_hit(self):
        result = classify_llm_hit("gpt-4o-mini", "path/api.xml")
        assert result["classification"] == "extracted_nuget_documentation"
        assert result["is_pipeline_call"] is False

    def test_approved_provider_hit(self):
        result = classify_llm_hit("using llm_professionalize", "config.py")
        assert result["classification"] == "approved_llm_provider_config"
        assert result["is_pipeline_call"] is True

    def test_unapproved_provider_hit(self):
        result = classify_llm_hit("using openai client", "bad.py")
        assert result["classification"] == "violation_unapproved_provider"
        assert result["is_pipeline_call"] is True

    def test_ambiguous_hit(self):
        result = classify_llm_hit("some random text", "file.py")
        assert result["classification"] == "ambiguous_needs_fix"
        assert result["is_pipeline_call"] is None
