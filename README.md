# 🚀 Tiny LLM Chat Agent

[![Codecov Coverage](https://codecov.io/gh/hieunq95/tiny-llm-agent/branch/main/graph/badge.svg)](https://app.codecov.io/gh/hieunq95/tiny-llm-agent)

A **FastAPI + Streamlit** based **Retrieval-Augmented Generation (RAG) chatbot**, designed to chat with users using local **large language models (LLMs)** while allowing **PDF uploads** for context-aware conversations. The system leverages the **Qwen-2.5:0.5B-Instruct** model, a lightweight LLM optimized for **efficient on-device processing**. This minimum setup ensures **fast response times** while enabling **customized knowledge retrieval** from uploaded documents, making it ideal for research, study, and technical applications.

**Disclaimer**: The `tiny-llm-agent` is provided for the demonstration purpose. It is implemented to run on CPU to ensure compatibility with most hardware devices. Additionally, the response length is limited to a fixed number of tokens because the small LLM cannot efficiently handle very long contexts. Expanding beyond these limitations can be achieved by using a larger model (e.g., Qwen2.5-7B) and enabling GPU processing for faster responses. See [rag-pipeline/notebooks/poc-rag-code.ipynb](rag-pipeline/notebooks/poc-rag-code.ipynb), [rag-pipeline/src/main.py](rag-pipeline/src/main.py), and [rag-pipeline/Dockerfile](rag-pipeline/Dockerfile) for detailed implementation and configuration.

**Architecture** of the platform is as follows:   
<img src="assets/architecture.png" alt="architecture" width="1024"/>  

The MLOps system illustrated in the image operates through two distinct pipelines:  
- **For developers**, the workflow begins with pushing code to a source control system (step 1), triggering a CI/CD pipeline (steps 2). The CI/CD pipeline builds, tests, and deploys containers locally. After that, it pushes Docker images to Docker Hub registry (step 3). These images are then pulled in a Kubernetes cluster on Google Cloud (step 4). Once the services start, the LLM will be downloaded from HuggingFace model registry and stored in the cluster (step 5).  
- **For users**, interactions start with a query from user (step 1), which routes requests through an API gateway (steps 2). The system generates embeddings (step 3), retrieves relevant vectors from the FAISS database (step 4), and returns a response (step 5). The API gateway finally forward the response and display it via Streamlit UI. 

**Mornitoring services** are managed by developers using `Jaeger`, `Prometheus`, and `Grafana`, ensuring observability for users.


  
## 📌 Features
✅ **FastAPI backend** to handle local LLM inference and document retrieval.  
✅ **Streamlit frontend** for lightweight and interactive chat experience.  
✅ **RAG support** to enrich personalized chat experience.  
✅ **Automatic deployment** with Docker and Kubernetes.  
✅ **LLM runs locally**, no external APIs required.  
✅ **Monitoring services** provide dashboards that measure system performance (e.g., chat response time, CPU usage) using Prometheus, Grafana, and Jaeger tracing.  
✅ **CI/CD** for automatic testing and building containers with Jenkins.  
✅ **Cloud support** for hosting LLM on Google Cloud Platform using Google Kubernetes Engine.

---

## 📂 Project Structure
```
tiny-llm-agent/  
│── docker-compose.yaml       # Docker setup for backend & frontend  
│── Jenkinsfile               # Jenkinsfile for CI/CD pipeline
│
├─ rag-pipeline/              # Backend (FastAPI)  
│ ├─── vector_store/          # Vector database (FAISS)  
│ ├─── examples/              # Example PDF files  
│ ├─── models/                # Local model storage  
│ ├─── notebooks/             # Notebooks for PoCs  
│ ├─── src/                   # Source code  
│ ├─── test/                  # Pytest code 
│ ├─── uploaded_pdfs/         # Uploaded user PDFs  
│ ├─── vector_store/          # FAISS vector database  
│ ├─── Dockerfile             # Backend Docker configuration  
│ ├─── requirements.txt       # Backend dependencies  
│
├─ streamlit/                 # Frontend (Streamlit)  
│ ├─── main.py                # Streamlit UI logic  
│ ├─── requirements.txt       # Frontend dependencies  
│ ├─── Dockerfile             # Frontend Docker configuration  
│  
├─ nginx/                     # API gateway configuration
│
├─ grafana/                   # Monitoring service (Grafana)  
│
├─ prometheus/                # Scraping metrics from backend (Prometheus)  
│
├─ jenkins/                   # CI/CD pipeline using Jenkins
│
├─ kubernetes/                # Local deployment & cloud deployment
│  
└── README.md                 # Project Documentation  

```

## 📦 Project Dependencies
- Docker desktop version 27.3.1  
- Docker Compose version v2.30.3-desktop.1  
- Kubectl version v1.32.2
- Helm version v3.17.1  

## 📖 Table of Contents
- [1. Local Deployment Using Docker](#1-local-deployment-using-docker)
  - [Clone the Repository](#clone-the-repository)
  - [Deployment with Docker](#deployment-with-docker)
  - [FastAPI Backend](#fastapi-backend)
  - [Streamlit UI](#streamlit-ui)
- [2. Monitoring Services](#2-monitoring-services)
  - [Prometheus](#prometheus)
  - [Grafana](#grafana)
  - [Jaeger tracing](#jaeger-tracing)
- [3. CI/CD](#3-cicd)
- [4. Google Cloud Deployment](#4-google-cloud-deployment)
---

## 1. Local Deployment Using Docker
### Clone the Repository
```bash
git clone https://github.com/hieunq95/tiny-llm-agent.git
cd tiny-llm-agent
```

### Deployment with Docker
Using `docker` desktop version `27.3.1`, run: 
```bash
docker-compose up --build
```  

Once running:
```bash
Backend (FastAPI) → http://localhost:8000/docs
Frontend (Streamlit) → http://localhost:8501
Monitoring (Prometheus) → http://localhost:9090
Dashboard (Grafana) → http://localhost:3000  
Distributed Tracing (Jaeger Tracing) → http://localhost:16686 
Proxy server (Nginx) → http://localhost:8080 
```

#### To stop:

```bash
docker-compose down -v
```

#### To rebuild:  
Delete Docker images (optional):
```bash
docker image remove -f $(docker images -aq)
```
Rebuild new images:
```bash
docker-compose up --build
```

### FastAPI Backend
Access FastAPI documentation at `http://localhost:8000/docs`.  
Select one entry, e.g., `api/upload_pdf`, and then select `Try it out` to send a `post` message to the backend server.
![](assets/fast_api.png)

### Streamlit UI  
Go to `http://localhost:8501/`, enter your user name, upload PDF file, and start chatting with the Tiny LLM Chat Agent.
![](assets/streamlit.png)

Note: If error `Device or resource busy: '/rag-pipeline/vector_store` appears when uploading a PDF, it may be due to vector storage being in use. Simply retry the upload.  

---

## 2. Monitoring Services

### Prometheus
Scrape metrics, such as LLM response latency, CPU/GPU usage, etc, from the backend.
![](assets/prometheus.png)


### Grafana
Dashboard: Visualize LLM response latency, CPU/GPU usage.  
See [grafana/README.md](grafana/README.md) for quick visualization set up.
![](assets/grafana.png)

### Jaeger tracing
Use Jaeger tracing to monitor and troubleshoot request flows of the services.  
![](assets/jaeger.png)

## 3. CI/CD
The CI/CD pipeline is triggered by GitHub commits from developers. It will run code coverage check with `pytest`. If the code coverage pass the threshold (80%), it uploads code coverage report to [Codecov.io](https://about.codecov.io/). An example of the log output from Jenkins pipeline is shown in the image below. 
Details on building CI/CD pipeline with Jenkins can be found in [jenkins](jenkins/README.md) directory. 

![](assets/cicd.png)

## 4. Google Cloud Deployment
- Details about deploying all services on a Google Cloud Platform (GCP) can be found in the [kubernetes](kubernetes/README.md) directory.  

- For a quick demo of the `tiny-llm-agent` chatbot on GCP, see video recap below. For the full video demo, check this [YouTube](https://www.youtube.com/watch?v=MBjAibP9fs8) link.  

![](assets/gcp-demo.gif)