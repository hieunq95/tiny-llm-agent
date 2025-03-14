import os
import shutil
import psutil
import time
import logging
import threading
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from pydantic import BaseModel
from data_pipeline import setup_pipeline
from model_setup import load_model
from utils import get_model_dir

# Prometheus metrics
REQUEST_COUNT = Counter("chatbot_requests_total", "Total requests to chatbot")
LATENCY = Histogram("chatbot_request_latency_seconds", "Chatbot request latency")
MODEL_LOAD_TIME = Histogram("chatbot_model_load_time_seconds", "Time to load the local LLM in secods")
MEMORY_USAGE = Gauge("chatbot_memory_usage_bytes", "Memory usage in bytes for chatbot process")

# LLM global variables
LLM_LOADED = False
qa_pipeline = None
model = None

# Define paths
UPLOAD_DIR = Path("./uploaded_pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_llm():
    """Function to load LLM on startup.
    """
    start_time = time.time()
    global qa_pipeline, LLM_LOADED, model
    
    try:
        # Loading LLM Model
        logger.info("🔄 Loading LLM ...")
        model = load_model(model_name="Qwen/Qwen2.5-0.5B-Instruct", local_dir=get_model_dir())
        MODEL_LOAD_TIME.observe(time.time() - start_time)
        LLM_LOADED = True
        logger.info("✅ LLM Model Loaded Successfully")
    except Exception as e:
        logger.error(f"❌ LLM Model Load Failed: {e}", exc_info=True)
        LLM_LOADED = False
        
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

class ChatRequest(BaseModel):
    messages: str

app = FastAPI()

@app.get("/metadata")
def get_metadata():
    return {"my_metadata": "This is a metadata endpoint."}

@app.get("/health")
async def health_check(response: Response):
    global LLM_LOADED
    health_status = {"status": "healthy"}
    
    if not LLM_LOADED:
        response.status_code = 503
        health_status["status"] = "unhealthy"
        
    return health_status

@app.post("/api/upload_pdf", description="API endpoint to upload PDF documents.")
async def upload_pdf(user_id: str, file: UploadFile = File(...)):
    """Handle PDF upload, extracts text, and updates the vector database.

    Args:
        user_id (str): User ID for storing and retrieving PDF documents.
        file (UploadFile, optional): PDF file to be uploaded. Defaults to File(...).
    """
    global qa_pipeline, model # Allow updating the retriever dynamically
    
    if not LLM_LOADED:
        raise HTTPException(status_code=503, detail="LLM is still loading. Please wait.")
    
    try:
        # Save file locally
        file_path = UPLOAD_DIR / f"{user_id}_{file.filename}"
        os.makedirs("./uploaded_pdfs", exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update qa_pipeline with the new document
        logger.info(f" Updating retriever for user {user_id}...")
        qa_pipeline = setup_pipeline(local_dir=get_model_dir(), file_path=str(file_path), model=model)
        logger.info("Retriever updated!")
        return {"message": "PDF processed and stored successfully", "file_path": file_path}

    except Exception as e:
        logger.error(f"❌ Error updating retriever: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/chat", description="API endpoint to chat with local LLM and measure latency with Prometheus.")
def chat_endpoint(user_id: str, request: ChatRequest):
    """Chat with the local LLM.

    Args:
        user_id (str): User ID.
        request (ChatRequest): Prompt to chat with the LLM.

    Returns:
        Response (json): {"response": answer of the LLM}.
    """
    REQUEST_COUNT.inc()
    start_time = time.time()
    global qa_pipeline # Ensure we use the latest retriever
    
    if not LLM_LOADED:
        raise HTTPException(status_code=503, detail="LLM is still loading. Please wait.")
    
    user_pdfs = sorted(UPLOAD_DIR.glob(f"{user_id}_*.pdf"), key=os.path.getmtime, reverse=True)
    latest_pdf = str(user_pdfs[0])
    
    # Ensure retriever is ready
    if qa_pipeline is None:
        raise HTTPException(status_code=503, detail="QA pipeline is not ready.")
    
    logger.info(f"Processing chat request using PDF: {latest_pdf}")
    
    response = qa_pipeline.invoke(request.messages)
    response_text = response["result"].split("Answer:")[-1].strip()
    
    LATENCY.observe(time.time() - start_time)
    return {"response": response_text}
    
@app.get("/api/config")
def get_config():
    return {
        "backend_name": "rag-pipeline",
        "models": [{"id": "qwen", "name": "Qwen 2.5 Instruct"}],
    }
    
@app.get("/metrics", description="Prometheus client's metrics.")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Main script for running local LLM with FastAPI.")
    parser.add_argument('--port', type=int, default=8000,
                        help="Port for FastAPI"
                        )
    args = parser.parse_args()
    
    # Load local LLM
    load_llm()
    
    # Start memory monitoring in a separate thread
    threading.Thread(target=monitor_memory_usage, daemon=True).start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=args.port)