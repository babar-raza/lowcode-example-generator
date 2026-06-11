"""LLM Provider Policy — approved provider enforcement.

Approved provider families: llm_professionalize, ollama
Forbidden provider families: gpt_oss, openai, azure_openai

A model name is NOT a provider family. gpt_oss may appear as a model name
configured under the ollama provider, but must never appear as a provider family.
"""

from __future__ import annotations

APPROVED_PROVIDERS: frozenset[str] = frozenset({"llm_professionalize", "ollama"})
UNAPPROVED_PROVIDERS: frozenset[str] = frozenset({"gpt_oss", "openai", "azure_openai"})
FORBIDDEN_PIPELINE_MODELS: frozenset[str] = frozenset({"gpt-4o-mini"})


def get_policy_violations(provider_order: list[str]) -> list[str]:
    """Return providers in provider_order that violate the approved policy."""
    return [p for p in provider_order if p in UNAPPROVED_PROVIDERS]


def filter_to_approved(provider_order: list[str]) -> list[str]:
    """Return only approved providers from provider_order."""
    return [p for p in provider_order if p in APPROVED_PROVIDERS]


def classify_provider_hit(location: str, provider: str, context: str) -> dict:
    """Classify a provider hit for audit purposes.

    Returns a dict with keys: location, provider, context, classification, approved.
    """
    if provider in APPROVED_PROVIDERS:
        classification = "approved_llm_provider_config"
    elif provider in UNAPPROVED_PROVIDERS:
        classification = "violation_unapproved_provider"
    else:
        classification = "unknown"
    return {
        "location": location,
        "provider": provider,
        "context": context,
        "classification": classification,
        "approved": provider in APPROVED_PROVIDERS,
    }


def is_forbidden_model(model_name: str) -> bool:
    """Return True if model_name is forbidden as a configured pipeline model.

    gpt-4o-mini is forbidden as a pipeline model.
    Note: model names (including gpt_oss appearing as a model name under ollama)
    are separate from provider families.
    """
    return model_name in FORBIDDEN_PIPELINE_MODELS


def classify_documentation_hit(text: str, location: str) -> dict:
    """Classify a text hit found inside extracted NuGet XML documentation.

    Returns classification='extracted_nuget_documentation' for .xml paths
    or paths containing nuget/extracted indicators.
    Returns 'ambiguous_needs_fix' otherwise.

    IMPORTANT: extracted_nuget_documentation hits are NOT pipeline LLM calls.
    A model name (e.g. gpt-4o-mini) found inside Aspose.Words.xml is Aspose's
    own API documentation code example — not a pipeline call.
    """
    is_xml_doc = (
        location.endswith(".xml") or "/nuget/" in location or "\\nuget\\" in location or "extracted" in location.lower()
    )
    return {
        "location": location,
        "text_snippet": text[:120],
        "classification": "extracted_nuget_documentation" if is_xml_doc else "ambiguous_needs_fix",
        "is_pipeline_call": False,
    }


def is_direct_openai_construction(source_text: str, file_path: str) -> bool:
    """Return True if source_text contains OpenAI( outside the approved provider module.

    Direct OpenAI Python client construction (OpenAI(...)) is allowed ONLY in:
        src/plugin_examples/llm_router/providers/professionalize.py

    It is forbidden in all other files, including router.py.

    Note: router.py currently uses requests.post/get (HTTP), not the OpenAI Python SDK.
    If an OpenAI( call is found outside the approved path, it is a policy violation.
    """
    APPROVED_PATHS = (
        "llm_router/providers/professionalize.py",
        "llm_router\\providers\\professionalize.py",
    )
    if any(approved in file_path for approved in APPROVED_PATHS):
        return False
    return "OpenAI(" in source_text


def validate_provider_family(provider_family: str) -> list[str]:
    """Validate a provider family against the approved list.

    Returns a list of violation messages. Empty list = valid.
    """
    violations = []
    if provider_family not in APPROVED_PROVIDERS:
        violations.append(
            f"Provider family '{provider_family}' is not approved. " f"Approved: {sorted(APPROVED_PROVIDERS)}"
        )
    if provider_family in UNAPPROVED_PROVIDERS:
        violations.append(f"Provider family '{provider_family}' is explicitly forbidden.")
    return violations


def validate_model_for_provider(provider_family: str, model_name: str) -> list[str]:
    """Validate a model name for a given provider family.

    Returns a list of violation messages. Empty list = valid.

    gpt-4o-mini is forbidden as a configured pipeline model regardless of provider.
    gpt_oss appearing as a model name under ollama is acceptable (not a provider family).
    """
    violations = []
    if model_name in FORBIDDEN_PIPELINE_MODELS:
        violations.append(
            f"Model '{model_name}' is forbidden as a configured pipeline model. " "Remove it from configuration."
        )
    return violations


def classify_llm_hit(text: str, location: str) -> dict:
    """Classify any LLM-related text hit for audit purposes.

    Combines documentation detection and provider/model classification.
    Returns a classification dict suitable for the LLM provider policy audit.
    """
    # Extracted NuGet XML documentation: not a pipeline call
    is_xml_doc = (
        location.endswith(".xml") or "/nuget/" in location or "\\nuget\\" in location or "extracted" in location.lower()
    )
    if is_xml_doc:
        return {
            "location": location,
            "text_snippet": text[:120],
            "classification": "extracted_nuget_documentation",
            "is_pipeline_call": False,
        }
    # Approved provider family reference
    for provider in APPROVED_PROVIDERS:
        if provider in text:
            return {
                "location": location,
                "text_snippet": text[:120],
                "classification": "approved_llm_provider_config",
                "is_pipeline_call": True,
            }
    # Unapproved provider family reference
    for provider in UNAPPROVED_PROVIDERS:
        if provider in text:
            return {
                "location": location,
                "text_snippet": text[:120],
                "classification": "violation_unapproved_provider",
                "is_pipeline_call": True,
            }
    return {
        "location": location,
        "text_snippet": text[:120],
        "classification": "ambiguous_needs_fix",
        "is_pipeline_call": None,
    }
