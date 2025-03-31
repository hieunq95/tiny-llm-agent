import pytest
from unittest.mock import patch, MagicMock
from transformers import AutoTokenizer, pipeline
from transformers.modeling_utils import PreTrainedModel
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from model_setup import load_model
from data_pipeline import setup_pipeline, chat_with_llm
from utils import get_model_dir, get_doc_dir

@pytest.fixture
def mock_setup_pipeline():
    with patch("data_pipeline.setup_pipeline") as mock_setup_pipeline:
        mock_qa_chain = MagicMock()
        mock_setup_pipeline.return_value = mock_qa_chain
        yield mock_setup_pipeline

def test_setup_pipeline():
    local_dir = get_model_dir()
    file_path = get_doc_dir()
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    model = load_model(model_name, local_dir)
    qa_chain = setup_pipeline(local_dir, file_path, model)
    assert isinstance(qa_chain, RetrievalQA)
    
def test_chat_with_llm(mock_setup_pipeline):
    test_question = "What is the capital of France?"
    expected_answer = "Paris"
    
    mock_qa_chain = MagicMock()
    mock_qa_chain.return_value = {
        "result": f"Here is the answer: Answer: {expected_answer}"
    }
    
    mock_setup_pipeline.return_value = mock_qa_chain
    answer = chat_with_llm(test_question)
    
    assert answer == expected_answer
    mock_setup_pipeline.assert_called_once_with(local_dir=get_model_dir())
    mock_qa_chain.assert_called_once_with(test_question)
    
    

    

    
    
    
    