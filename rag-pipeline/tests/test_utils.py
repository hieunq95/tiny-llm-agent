import pytest
import time
from threading import Thread
from unittest.mock import patch, MagicMock
from utils import get_hardware, get_model_dir, get_doc_dir, monitor_memory_usage


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

def test_monitor_memory_usage():
    thread = Thread(target=monitor_memory_usage, kwargs={"interval": 0.1})
    thread.daemon = True 
    thread.start()
    time.sleep(0.5)
    assert thread.is_alive()
    