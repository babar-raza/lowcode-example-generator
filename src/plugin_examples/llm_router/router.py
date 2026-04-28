"""LLM provider routing with preflight validation."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


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
        return _call_provider(provider, prompt, system_prompt=system_prompt, timeout=timeout)


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


def _check_provider(provider: str, *, timeout: int = 30, config: dict | None = None) -> PreflightResult:
    """Check a single provider's availability."""
    result = PreflightResult(provider=provider)

    try:
        endpoint = _get_endpoint(provider, config)
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
    defaults = {
        "ollama": "http://localhost:11434/api/tags",
        "llm_professionalize": "http://localhost:8080/v1/models",
    }
    return defaults.get(provider, f"http://localhost:8080/{provider}")


def _call_provider(provider: str, prompt: str, *, system_prompt: str = "", timeout: int = 120) -> str:
    """Call an LLM provider to generate text."""
    if provider == "ollama":
        return _call_ollama(prompt, system_prompt=system_prompt, timeout=timeout)
    elif provider == "llm_professionalize":
        return _call_openai_compatible(
            "http://localhost:8080/v1/chat/completions",
            prompt, system_prompt=system_prompt, timeout=timeout,
        )
    else:
        raise LLMProviderError(f"Unknown provider: {provider}")


def _call_ollama(prompt: str, *, system_prompt: str = "", timeout: int = 120) -> str:
    """Call Ollama API."""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "codellama", "prompt": prompt, "system": system_prompt, "stream": False},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def _call_openai_compatible(endpoint: str, prompt: str, *, system_prompt: str = "", timeout: int = 120) -> str:
    """Call OpenAI-compatible API."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        endpoint,
        json={"messages": messages, "temperature": 0.2},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
