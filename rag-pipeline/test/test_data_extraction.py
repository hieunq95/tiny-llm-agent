import os
import pytest
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils import get_doc_dir
from data_extraction import extract_data

def test_pdf_loader():
    """Test the PyPDFLoader class."""
    pdf_path = get_doc_dir()  # get document path from utils.py
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    print("docs:", docs)
    assert len(docs) > 1
    assert len(docs[0].page_content) > 0
    
def test_text_splitter():
    """Test the RecursiveCharacterTextSplitter class."""
    text = "This is a test sentence. This is another test sentence."
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=5)
    chunks = text_splitter.split_text(text)
    assert chunks[0] == "This is a"
    assert chunks[-1] == "sentence."
    
def test_full_processing_loop():
    """Test creating chunks of text"""
    chunk = extract_data(get_doc_dir())
    assert len(chunk) > 0
    assert isinstance(chunk, list)
    assert isinstance(chunk[0], str)
    
    