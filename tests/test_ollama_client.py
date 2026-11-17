"""
Unit Tests for FITGEN AI Ollama Client.
Mocks HTTP network interactions to verify connection failure, timeouts, and error handling.
"""

from unittest.mock import patch, MagicMock
import pytest
import requests
from core.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    OllamaError,
)


def test_ollama_health_check_offline():
    """Verify health check returns offline state when connection is refused."""
    client = OllamaClient(base_url="http://localhost:11434")
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection refused")):
        is_online, msg, models = client.check_health()
        assert is_online is False
        assert "Cannot connect to Ollama" in msg
        assert models == []


def test_ollama_health_check_online():
    """Verify health check detects online server and installed models."""
    client = OllamaClient(base_url="http://localhost:11434", default_model="llama3.2")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "llama3.2:latest"}, {"name": "mistral:latest"}]
    }

    with patch("requests.get", return_value=mock_resp):
        is_online, msg, models = client.check_health()
        assert is_online is True
        assert len(models) == 2
        assert "ready" in msg


def test_ollama_generate_connection_error():
    """Verify generate raises OllamaConnectionError when server is unreachable."""
    client = OllamaClient(base_url="http://localhost:11434")
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Offline")):
        with pytest.raises(OllamaConnectionError, match="Failed to connect to Ollama"):
            client.generate(prompt="Test prompt")


def test_ollama_generate_model_not_found():
    """Verify generate raises OllamaModelNotFoundError on HTTP 404."""
    client = OllamaClient(base_url="http://localhost:11434")
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(OllamaModelNotFoundError, match="not found on Ollama server"):
            client.generate(prompt="Test prompt", model="nonexistent-model")


def test_ollama_generate_timeout():
    """Verify generate raises OllamaTimeoutError on request timeout."""
    client = OllamaClient(base_url="http://localhost:11434", timeout=5)
    with patch("requests.post", side_effect=requests.exceptions.Timeout("Timed out")):
        with pytest.raises(OllamaTimeoutError, match="exceeded timeout"):
            client.generate(prompt="Test prompt")


def test_ollama_generate_empty_response():
    """Verify generate raises OllamaError when model returns empty response string."""
    client = OllamaClient(base_url="http://localhost:11434")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": ""}
    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(OllamaError, match="empty response string"):
            client.generate(prompt="Test prompt")
