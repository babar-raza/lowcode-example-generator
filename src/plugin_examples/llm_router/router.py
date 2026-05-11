"""LLM provider routing with preflight validation."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# Backoff delays (seconds) between retry attempts 1→2 and 2→3.
# Tests may patch this list with [0, 0] to avoid sleeping.
_LLM_RETRY_BACKOFF_SECONDS: list[int] = [30, 60]

# Maximum number of retry attempts on transient timeout/connection errors.
_LLM_MAX_RETRIES: int = 2


class LLMProviderError(Exception):
    """Raised when no LLM provider is available."""


@dataclass
class PreflightResult:
    """Result of a single provider preflight check."""
    provider: str
    endpoint_reachable: bool = False
    model_available: bool = False
    json_response: bool = False
    structured_response_parseable: bool = False
    timeout_within_limit: bool = False
    latency_ms: float = 0.0
    error: str | None = None

    @property
    def passed(self) -> bool:
        return all([
            self.endpoint_reachable,
            self.model_available,
            self.json_response,
            self.structured_response_parseable,
            self.timeout_within_limit,
        ])


@dataclass
class LLMRouter:
    """Route LLM requests to available providers."""
    provider_order: list[str] = field(default_factory=list)
    preflight_results: list[PreflightResult] = field(default_factory=list)
    selected_provider: str | None = None
    metrics_collector: object | None = None  # Optional MetricsCollector instance

    def run_preflight(
        self,
        *,
        timeout: int = 30,
        llm_config: dict | None = None,
    ) -> list[PreflightResult]:
        """Run preflight checks on all configured providers.

        Args:
            timeout: Request timeout in seconds.
            llm_config: Optional LLM routing config dict.

        Returns:
            List of preflight results, one per provider.
        """
        self.preflight_results = []

        for provider in self.provider_order:
            result = _check_provider(provider, timeout=timeout, config=llm_config)
            self.preflight_results.append(result)

            if result.passed:
                self.selected_provider = provider
                logger.info("LLM provider selected: %s (%.0fms)", provider, result.latency_ms)
                break

        if not self.selected_provider:
            logger.warning("No LLM provider passed preflight")

        return self.preflight_results

    def get_provider(self) -> str:
        """Get the selected provider, raising if none available."""
        if not self.selected_provider:
            raise LLMProviderError(
                "No LLM provider passed preflight. "
                f"Tried: {', '.join(self.provider_order)}"
            )
        return self.selected_provider

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        timeout: int = 120,
    ) -> str:
        """Generate text using the selected provider.

        Args:
            prompt: User prompt.
            system_prompt: System prompt.
            timeout: Request timeout.

        Returns:
            Generated text response.
        """
        provider = self.get_provider()
        return _call_provider(
            provider, prompt, system_prompt=system_prompt, timeout=timeout,
            metrics_collector=self.metrics_collector,
        )


def write_preflight_report(
    results: list[PreflightResult],
    selected: str | None,
    verification_dir: Path,
) -> Path:
    """Write LLM preflight report."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "llm-preflight.json"

    data = {
        "selected_provider": selected,
        "provider_family": selected,
        "provider_base_url": _get_provider_base_url(selected),
        "model_name": _get_provider_model(selected),
        "route": _route_label(selected),
        "preflight_passed": selected is not None,
        "called_by_stage": "preflight",
        "request_count": 1 if selected else 0,
        "documentation_hits_excluded": True,
        "classification_notes": (
            "Model names found inside extracted NuGet XML documentation are classified as "
            "extracted_nuget_documentation and are not pipeline LLM calls"
        ),
        "results": [
            {
                "provider": r.provider,
                "passed": r.passed,
                "endpoint_reachable": r.endpoint_reachable,
                "model_available": r.model_available,
                "json_response": r.json_response,
                "structured_response_parseable": r.structured_response_parseable,
                "timeout_within_limit": r.timeout_within_limit,
                "latency_ms": r.latency_ms,
                "error": r.error,
            }
            for r in results
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("LLM preflight report written: %s", path)
    return path


def _resolve_api_key(provider: str) -> str:
    """Resolve API key from environment for a provider."""
    if provider in ("gpt_oss", "llm_professionalize"):
        return os.environ.get("GPT_OSS_API_KEY") or os.environ.get("LLM_API_KEY", "")
    # openai or generic
    return os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")


def _check_provider(provider: str, *, timeout: int = 30, config: dict | None = None) -> PreflightResult:
    """Check a single provider's availability."""
    result = PreflightResult(provider=provider)
    # Policy enforcement: reject unapproved providers at preflight so they are never selected.
    # This must mirror the guard in _call_provider — both layers must enforce the same policy.
    if provider not in _APPROVED_PROVIDER_FAMILIES:
        result.error = (
            f"Provider family '{provider}' is not approved by policy. "
            f"Approved: {sorted(_APPROVED_PROVIDER_FAMILIES)}"
        )
        return result  # passed=False (all boolean fields default to False)

    try:
        endpoint = _get_endpoint(provider, config)

        # API-key providers: check key presence + models endpoint
        if provider in ("openai", "gpt_oss", "llm_professionalize"):
            api_key = _resolve_api_key(provider)
            if not api_key:
                result.error = f"No API key for {provider}"
                return result
            start = time.time()
            resp = requests.get(
                endpoint, headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout,
            )
        else:
            start = time.time()
            resp = requests.get(endpoint, timeout=timeout)

        result.latency_ms = (time.time() - start) * 1000
        result.timeout_within_limit = result.latency_ms < (timeout * 1000)
        result.endpoint_reachable = resp.status_code < 500
        result.model_available = resp.status_code == 200

        try:
            resp.json()
            result.json_response = True
            result.structured_response_parseable = True
        except (ValueError, json.JSONDecodeError):
            result.json_response = False

    except requests.exceptions.ConnectionError:
        result.error = f"Connection refused: {provider}"
    except requests.exceptions.Timeout:
        result.error = f"Timeout: {provider}"
    except Exception as e:
        result.error = str(e)

    return result


def _get_endpoint(provider: str, config: dict | None) -> str:
    """Get the endpoint URL for a provider."""
    if config and "providers" in config:
        for p in config["providers"]:
            if p.get("name") == provider:
                return p.get("endpoint", "")

    # Default endpoints
    gpt_oss_base = os.environ.get("GPT_OSS_ENDPOINT", "https://api.openai.com/v1/").rstrip("/")
    defaults = {
        "ollama": "http://localhost:11434/api/tags",
        "llm_professionalize": f"{gpt_oss_base}/models",
        "openai": "https://api.openai.com/v1/models",
        "gpt_oss": f"{gpt_oss_base}/models",
    }
    return defaults.get(provider, f"http://localhost:8080/{provider}")


_APPROVED_PROVIDER_FAMILIES: frozenset[str] = frozenset({"llm_professionalize", "ollama"})


def _get_provider_base_url(provider: str | None) -> str | None:
    """Return the base URL for a known provider."""
    if provider == "llm_professionalize":
        return os.environ.get("GPT_OSS_ENDPOINT", "https://llm.professionalize.com/v1/")
    if provider == "ollama":
        return os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    return None


def _get_provider_model(provider: str | None) -> str | None:
    """Return the configured model name for a known provider."""
    if provider == "llm_professionalize":
        return os.environ.get("GPT_OSS_MODEL", "recommended")
    if provider == "ollama":
        return "codellama"
    return None


def _route_label(provider: str | None) -> str:
    """Map provider name to canonical route label for evidence reporting."""
    if provider == "llm_professionalize":
        return "llm_professionalize"
    if provider == "ollama":
        return "local_ollama"
    return "none"


def _call_provider(
    provider: str, prompt: str, *, system_prompt: str = "", timeout: int = 120,
    metrics_collector: object | None = None,
) -> str:
    """Call an LLM provider to generate text."""
    if provider not in _APPROVED_PROVIDER_FAMILIES:
        raise LLMProviderError(
            f"Provider family '{provider}' is not approved by policy. "
            f"Approved: {sorted(_APPROVED_PROVIDER_FAMILIES)}"
        )
    if provider == "ollama":
        return _call_ollama(prompt, system_prompt=system_prompt, timeout=timeout,
                            metrics_collector=metrics_collector)
    elif provider == "llm_professionalize":
        api_key = _resolve_api_key("llm_professionalize")
        base = os.environ.get("GPT_OSS_ENDPOINT", "http://localhost:8080/v1/").rstrip("/")
        model = os.environ.get("GPT_OSS_MODEL", "recommended")
        return _call_openai_compatible(
            f"{base}/chat/completions",
            prompt, system_prompt=system_prompt, timeout=timeout,
            api_key=api_key, model=model,
            metrics_collector=metrics_collector, metrics_provider=provider,
            metrics_model=model,
        )
    elif provider == "openai":
        api_key = _resolve_api_key("openai")
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        return _call_openai_compatible(
            "https://api.openai.com/v1/chat/completions",
            prompt, system_prompt=system_prompt, timeout=timeout,
            api_key=api_key, model=model,
            metrics_collector=metrics_collector, metrics_provider=provider,
            metrics_model=model,
        )
    elif provider == "gpt_oss":
        api_key = _resolve_api_key("gpt_oss")
        base = os.environ.get("GPT_OSS_ENDPOINT", "https://api.openai.com/v1/").rstrip("/")
        model = os.environ.get("GPT_OSS_MODEL", "recommended")
        return _call_openai_compatible(
            f"{base}/chat/completions",
            prompt, system_prompt=system_prompt, timeout=timeout,
            api_key=api_key, model=model,
            metrics_collector=metrics_collector, metrics_provider=provider,
            metrics_model=model,
        )
    else:
        raise LLMProviderError(f"Unknown provider: {provider}")


def _call_ollama(
    prompt: str, *, system_prompt: str = "", timeout: int = 120,
    metrics_collector: object | None = None,
) -> str:
    """Call Ollama API with retry on transient timeout/connection errors."""
    for attempt in range(_LLM_MAX_RETRIES + 1):
        start = time.time()
        http_status = None
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "codellama", "prompt": prompt, "system": system_prompt, "stream": False},
                timeout=timeout,
            )
            http_status = resp.status_code
            resp.raise_for_status()
            data = resp.json()
            result = data.get("response", "")
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            duration_ms = (time.time() - start) * 1000
            error_cat = "timeout" if isinstance(exc, requests.exceptions.Timeout) else "connection_error"
            if metrics_collector is not None and hasattr(metrics_collector, "record_call"):
                metrics_collector.record_call(
                    stage="", provider="ollama", model="codellama",
                    success=False, http_status=http_status,
                    prompt_tokens=0, completion_tokens=0, total_tokens=0,
                    token_usage_available=False, duration_ms=duration_ms,
                    error_category=error_cat,
                )
            if attempt < _LLM_MAX_RETRIES:
                delay = _LLM_RETRY_BACKOFF_SECONDS[attempt] if attempt < len(_LLM_RETRY_BACKOFF_SECONDS) else 60
                logger.warning(
                    "Ollama LLM call attempt %d/%d failed (%s), retrying in %ds",
                    attempt + 1, _LLM_MAX_RETRIES + 1, type(exc).__name__, delay,
                )
                time.sleep(delay)
                continue
            raise
        except Exception:
            if metrics_collector is not None and hasattr(metrics_collector, "record_call"):
                duration_ms = (time.time() - start) * 1000
                metrics_collector.record_call(
                    stage="", provider="ollama", model="codellama",
                    success=False, http_status=http_status,
                    prompt_tokens=0, completion_tokens=0, total_tokens=0,
                    token_usage_available=False, duration_ms=duration_ms,
                    error_category="request_failed",
                )
            raise

        if metrics_collector is not None and hasattr(metrics_collector, "record_call"):
            duration_ms = (time.time() - start) * 1000
            eval_count = data.get("eval_count", 0)
            prompt_eval = data.get("prompt_eval_count", 0)
            total = eval_count + prompt_eval
            metrics_collector.record_call(
                stage="", provider="ollama", model="codellama",
                success=True, http_status=http_status,
                prompt_tokens=prompt_eval, completion_tokens=eval_count,
                total_tokens=total,
                token_usage_available="eval_count" in data,
                duration_ms=duration_ms,
            )
        return result
    raise RuntimeError("Ollama LLM call failed after all retry attempts")


def _call_openai_compatible(
    endpoint: str,
    prompt: str,
    *,
    system_prompt: str = "",
    timeout: int = 120,
    api_key: str = "",
    model: str = "",
    metrics_collector: object | None = None,
    metrics_provider: str = "",
    metrics_model: str = "",
) -> str:
    """Call OpenAI-compatible API with retry on transient timeout/connection errors."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    body: dict = {"messages": messages, "temperature": 0.2}
    if model:
        body["model"] = model

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    for attempt in range(_LLM_MAX_RETRIES + 1):
        start = time.time()
        http_status = None
        try:
            resp = requests.post(endpoint, json=body, headers=headers, timeout=timeout)
            http_status = resp.status_code
            resp.raise_for_status()
            data = resp.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            duration_ms = (time.time() - start) * 1000
            error_cat = "timeout" if isinstance(exc, requests.exceptions.Timeout) else "connection_error"
            if metrics_collector is not None and hasattr(metrics_collector, "record_call"):
                metrics_collector.record_call(
                    stage="", provider=metrics_provider, model=metrics_model,
                    success=False, http_status=http_status,
                    prompt_tokens=0, completion_tokens=0, total_tokens=0,
                    token_usage_available=False, duration_ms=duration_ms,
                    error_category=error_cat,
                )
            if attempt < _LLM_MAX_RETRIES:
                delay = _LLM_RETRY_BACKOFF_SECONDS[attempt] if attempt < len(_LLM_RETRY_BACKOFF_SECONDS) else 60
                logger.warning(
                    "OpenAI-compatible LLM call attempt %d/%d failed (%s), retrying in %ds",
                    attempt + 1, _LLM_MAX_RETRIES + 1, type(exc).__name__, delay,
                )
                time.sleep(delay)
                continue
            raise
        except Exception:
            if metrics_collector is not None and hasattr(metrics_collector, "record_call"):
                duration_ms = (time.time() - start) * 1000
                metrics_collector.record_call(
                    stage="", provider=metrics_provider, model=metrics_model,
                    success=False, http_status=http_status,
                    prompt_tokens=0, completion_tokens=0, total_tokens=0,
                    token_usage_available=False, duration_ms=duration_ms,
                    error_category="request_failed",
                )
            raise

        content = data["choices"][0]["message"]["content"]

        if metrics_collector is not None and hasattr(metrics_collector, "record_call"):
            duration_ms = (time.time() - start) * 1000
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            metrics_collector.record_call(
                stage="", provider=metrics_provider, model=metrics_model,
                success=True, http_status=http_status,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                token_usage_available="usage" in data,
                duration_ms=duration_ms,
            )

        return content
    raise RuntimeError("OpenAI-compatible LLM call failed after all retry attempts")
