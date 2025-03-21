FROM python:3.10-slim AS build

WORKDIR /streamlit
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim
WORKDIR /streamlit
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]