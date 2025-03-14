import os
import torch

def get_hardware() -> str:
    """Get hardware available for inference.
    """
    hardware = "cpu"
    if torch.cuda.is_available():
        hardware = "cuda"
    else:
        if torch.backends.mps.is_available():
            hardware = "mps"
    return hardware

def get_root_dir() -> str:
    """Get root working directory of the project.
    """
    project_root = os.getenv(
        "PROJECT_ROOT", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        )
    return project_root
    

def get_model_dir() -> str:
    """Get directory of the saved LLM model
    """
    model_dir = os.path.join(get_root_dir(), "rag-pipeline/models/Qwen2.5-0.5B-Instruct")
    return model_dir

def get_doc_dir() -> str:
    """Get directory of the input PDF document.
    """
    doc_dir = os.path.join(get_root_dir(), "rag-pipeline/examples/example.pdf")
    return doc_dir