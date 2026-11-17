"""
Ollama Client Interface for FITGEN AI.
Connects to the local Ollama REST API with robust error handling, health checks, and configurable timeouts.
"""

import requests
from typing import Dict, Any, List, Tuple, Optional
from config.settings import settings


class OllamaError(Exception):
    """Base exception for Ollama interactions."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when Ollama daemon cannot be contacted."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Raised when requested LLM model is not pulled locally."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when generation exceeds timeout threshold."""
    pass


class OllamaClient:
    """Client for querying the local Ollama service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    def check_health(self) -> Tuple[bool, str, List[str]]:
        """
        Probe the local Ollama server.
        Returns: (is_online, status_message, list_of_installed_models)
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                if self.default_model in models or any(self.default_model in m for m in models):
                    return True, f"Ollama is online. Model '{self.default_model}' is ready.", models
                else:
                    return (
                        True,
                        f"Ollama is online, but '{self.default_model}' was not detected in downloaded models.",
                        models,
                    )
            return False, f"Ollama responded with HTTP {resp.status_code}.", []
        except requests.exceptions.ConnectionError:
            return (
                False,
                f"Cannot connect to Ollama at {self.base_url}. Ensure the Ollama daemon is running.",
                [],
            )
        except requests.exceptions.Timeout:
            return False, "Connection to Ollama timed out.", []
        except Exception as e:
            return False, f"Ollama probe error: {str(e)}", []

    def get_installed_models(self) -> List[str]:
        """Fetch list of local model names."""
        is_up, _, models = self.check_health()
        return models if is_up else []

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        format_json: bool = True,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Invoke Ollama generate endpoint.
        Returns raw response text.
        """
        target_model = model or self.default_model
        endpoint = f"{self.base_url}/api/generate"

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else settings.OLLAMA_TEMPERATURE,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        if format_json:
            payload["format"] = "json"

        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code == 404:
                raise OllamaModelNotFoundError(
                    f"Model '{target_model}' not found on Ollama server. Pull it using: `ollama pull {target_model}`"
                )

            if response.status_code != 200:
                raise OllamaError(
                    f"Ollama API returned HTTP {response.status_code}: {response.text}"
                )

            data = response.json()
            raw_response = data.get("response", "")
            if not raw_response:
                raise OllamaError("Ollama returned an empty response string.")

            return raw_response

        except requests.exceptions.ConnectionError:
            raise OllamaConnectionError(
                f"Failed to connect to Ollama at {self.base_url}. Please ensure Ollama is running (`ollama serve`)."
            )
        except requests.exceptions.Timeout:
            raise OllamaTimeoutError(
                f"Ollama generation exceeded timeout of {self.timeout} seconds. Consider simplifying the request or increasing OLLAMA_TIMEOUT."
            )
        except (OllamaError, OllamaConnectionError, OllamaModelNotFoundError, OllamaTimeoutError):
            raise
        except Exception as e:
            raise OllamaError(f"Unexpected error during Ollama generation: {str(e)}")
