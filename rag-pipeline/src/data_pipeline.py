from transformers import AutoTokenizer, pipeline
from transformers.modeling_utils import PreTrainedModel
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from model_setup import load_model
from data_preparation import prepare_retriever
from utils import get_model_dir

def setup_pipeline(local_dir: str, file_path: str = None, model: PreTrainedModel = None) -> RetrievalQA:
    """Setup a QA chain with RAG model.

    Args:
        local_dir (str): Directory of the local LLM model.
        file_path (str): File path to the PDF file.
        model (PreTrainedModel): Pre-loaded locam LLM model.

    Returns:
        RetrievalQA: A QA chain object.
    """
    tokenizer = AutoTokenizer.from_pretrained(local_dir)
    
    if model is None:
        model = load_model(
            model_name="Qwen/Qwen2.5-0.5B-Instruct", 
            local_dir=get_model_dir()
        )
    
    retriever = prepare_retriever(file_path=file_path)
    
    # Setup a RAG pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        repetition_penalty=1.2,
        max_new_tokens=256
    )
    
    # Wrap the HuggingFace pipeline in a LangChain object
    local_llm = HuggingFacePipeline(pipeline=pipe)
    
    # Define the prompt template
    prompt_template = """Answer based on context:\n{context}\nQuestion: {question}\nAnswer:"""
    prompt = PromptTemplate(
        input_variables=["contenxt", "question"],
        template=prompt_template
    )
    
    # Setup a QA chain
    qa_chain = RetrievalQA.from_chain_type(
    llm=local_llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt}
    )
    
    return qa_chain

def chat_with_llm(question: str):
    """Ask a question to the QA chain and return the response.

    Args:
        question (str): A question to ask.
    """
    # Setup a QA chain
    qa_chain = setup_pipeline(local_dir=get_model_dir())
    
    # Ask a question
    response = qa_chain(question)
    answer = response["result"].split("Answer:")[-1].strip()
    return answer

if __name__ == "__main__":
    # Ask a question
    question = "Describe the model architecture of the deep learning approach in the paper."
    answer = chat_with_llm(question)
    print("Answer:", answer)
