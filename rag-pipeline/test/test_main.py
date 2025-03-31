import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from unittest import TestCase
from main import app, model_state, load_llm
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

@pytest.fixture(autouse=True)
def kill_opentelemetry():
    """Prevent any OpenTelemetry initialization"""
    with patch("opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument_app"), \
         patch("opentelemetry.trace.get_tracer_provider"), \
         patch("opentelemetry.sdk.trace.export.SpanExporter"):
        yield

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_mocks():
    # Reset model state before each test
    model_state.llm_loaded = False
    model_state.qa_pipelines = {}
    model_state.model = MagicMock()
    yield
    
def test_get_config(test_client):
    response = test_client.get("api/config")
    assert response.status_code == 200
    assert response.json() == {
        "backend_name": "rag-pipeline",
        "models": [{"id": "qwen", "name": "Qwen 2.5 Instruct"}],
    }
    
def test_metrics(test_client):
    test_client.get("/health")
    test_client.get("/metadata")
    
    response = test_client.get("/metrics")
    assert response.status_code == 200
    assert "HELP" in response.text 
    
def test_metadata_endpoint(test_client):
    response = test_client.get("/metadata")
    assert response.status_code == 200
    assert response.json() == {"my_metadata": "This is a metadata endpoint."}
    
def test_health_check(test_client):
    model_state.llm_loaded = True
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    
    # Test unhealthy status
    model_state.llm_loaded = False
    response = test_client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy"}
    
@patch("main.setup_pipeline")
def test_upload_pdf(mock_setup, test_client):
    mock_setup.return_value = MagicMock()
    model_state.llm_loaded = True
    test_file = ("test.pdf", b"fake pdf content")
    response = test_client.post(
        "/api/upload_pdf?user_id=test_user",
        files={"file": test_file}
    )
    assert response.status_code == 200
    assert "file_path" in response.json()
    mock_setup.assert_called_once()
    
def test_chat_endpoint(test_client):
    model_state.llm_loaded = True
    model_state.qa_pipelines['test_user'] = MagicMock()
    model_state.qa_pipelines.get('test_user').invoke.return_value = {"result": "Answer: Paris"}
    
    response = test_client.post(
        "/api/chat?user_id=test_user",
        json={"messages": "Capital of France?"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"response": "Paris"}
    
@patch("utils.snapshot_download")
@patch("utils.AutoModelForCausalLM.from_pretrained")
def test_load_llm(mock_from_pretrained, mock_snapshot):
    # Mock model loading
    mock_from_pretrained.return_value = MagicMock()
    mock_snapshot.return_value = None

    model_state.llm_loaded = False

    load_llm()
    assert model_state.llm_loaded is True

    mock_from_pretrained.side_effect = Exception("Load failed")
    load_llm()
    assert model_state.llm_loaded is False