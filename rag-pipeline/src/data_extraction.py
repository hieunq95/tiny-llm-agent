from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils import get_doc_dir

def extract_data(pdf_path: str) -> list:
    """Extract text from a PDF document and return a list of text chunks.

    Args:
        pdf_path (str): Path to the pdf document.

    Returns:
        list: A list of text chunks.
    """
    # Load a PDF document
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()  # a list of Document objects
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks = []
    for doc in docs:
        chunk_list = text_splitter.split_text(doc.page_content)
        for chunk in chunk_list:
            chunks.append(chunk)
            
    return chunks

    
if __name__ == "__main__":
    chunks = extract_data(get_doc_dir())
    print("Number of text chunks:", len(chunks))
    print("Sample chunks:", chunks[:2])
    
