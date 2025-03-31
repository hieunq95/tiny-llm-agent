import os
import re
import torch
import psutil
import time
import logging
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM
from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

# Initialize OpenTelemetry
set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "rag-pipeline-service"}))
)
tracer = get_tracer_provider().get_tracer("rag-pipeline", "0.1.0")
jaeger_exporter = JaegerExporter(
    collector_endpoint="http://jaeger:14268/api/traces"
)
span_processor = BatchSpanProcessor(jaeger_exporter)
get_tracer_provider().add_span_processor(span_processor)

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
    

def get_model_dir(model_name: str = "Qwen/Qwen2.5-0.5B-Instruct") -> str:
    """Get directory of the saved LLM model

    Args:
        model_name (str, optional): Model name on [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct). 
        Defaults to "Qwen2.5-0.5B-Instruct".

    Returns:
        str: _description_
    """
    model_dir = os.path.join(get_root_dir(), "rag-pipeline/models/" + model_name)
    return model_dir

def get_doc_dir() -> str:
    """Get directory of the input PDF document.
    """
    doc_dir = os.path.join(get_root_dir(), "rag-pipeline/examples/example.pdf")
    return doc_dir

# Prometheus metrics
REQUEST_COUNT = Counter("chatbot_requests_total", "Total requests to chatbot")
LATENCY = Histogram("chatbot_request_latency_seconds", "Chatbot request latency")
MODEL_LOAD_TIME = Histogram("chatbot_model_load_time_seconds", "Time to load the local LLM in secods")
MEMORY_USAGE = Gauge("chatbot_memory_usage_bytes", "Memory usage in bytes for chatbot process")

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
        
def monitor_memory_usage(interval: int=5):
    """Get memory usage of the LLM.

    Args:
        interval (int, optional): Interval between memory usage report. Defaults to 5.
    """
    while True:
        try:
            process = psutil.Process()
            MEMORY_USAGE.set(process.memory_info().rss)  # Update Prometheus gauge
        except Exception as e:
            logger.error(f"Memory monitoring error: {e}", exc_info=True)
        time.sleep(interval)
        
def secure_filename(filename: str) -> str:
    """Secure filename sanitizer
    """
    # Remove path components and special characters
    clean = re.sub(r'(?u)[^-\w.]', '', filename.split("/")[-1])
    # Prevent empty filenames and hidden files
    return clean.lstrip('.') or 'document'