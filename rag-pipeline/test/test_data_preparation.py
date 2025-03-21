import pytest
import os
import hashlib
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores.base import VectorStoreRetriever
from data_preparation import compute_content_hash, get_vector_store, prepare_retriever
from utils import get_hardware, get_doc_dir

def test_compute_content_hash():
    """Test hash changes with content/model changes"""
    chunks = ["this is", "a test", "chunk"]
    embedding_model_name = "model-v1"
    
    # Original hash
    hash1 = compute_content_hash(chunks, embedding_model_name)
    
    # Test content change
    hash2 = compute_content_hash(chunks + ["new"], embedding_model_name)
    assert hash1 != hash2
    
    # Test model name change
    hash3 = compute_content_hash(chunks, "model-v2")
    assert hash1 != hash3
    
def test_get_vector_store():
    chunks = ["this is", "a test", "chunk"]
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    cache_dir = "vector_store"
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={"device": get_hardware()}
        )
    vector_store = get_vector_store(chunks, embeddings, cache_dir)
    assert isinstance(vector_store, FAISS)
    
def test_prepare_retriever():
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    file_path = get_doc_dir()
    retriever = prepare_retriever(embedding_model_name, file_path)
    assert isinstance(retriever, VectorStoreRetriever)
    