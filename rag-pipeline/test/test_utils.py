import pytest
import time
from threading import Thread
from unittest.mock import patch, MagicMock
from utils import (
    get_hardware, get_model_dir, get_doc_dir, ModelState, load_llm,
    monitor_memory_usage, model_state
)

@pytest.fixture(autouse=True)
def disable_tracing():
    """Disable OpenTelemetry tracing during tests."""
    with patch.dict("os.environ", {"DISABLE_TRACING": "true"}):
        yield
        
def test_get_hardware():
    with patch("torch.cuda.is_available", return_value=False), \
         patch("torch.backends.mps.is_available", return_value=False):
        assert get_hardware() == "cpu"
    
    with patch("torch.cuda.is_available", return_value=True):
        assert get_hardware() == "cuda"
        
    with patch("torch.cuda.is_available", return_value=False), \
         patch("torch.backends.mps.is_available", return_value=True):
        assert get_hardware() == "mps"
        
def test_get_root_dir():
    model_dir = get_model_dir()
    assert "rag-pipeline/models/Qwen" in model_dir
    
def test_get_doc_dir():
    doc_dir = get_doc_dir()
    assert "rag-pipeline/examples/example.pdf" in doc_dir
    
def test_model_state():
    state = ModelState()
    assert state.llm_loaded is False
    assert state.qa_pipeline is None
    assert state.model is None
    

def test_monitor_memory_usage():
    thread = Thread(target=monitor_memory_usage, kwargs={"interval": 0.1})
    thread.daemon = True 
    thread.start()
    time.sleep(0.5)
    assert thread.is_alive()
    
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
    