import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from config import configs
from dotenv import load_dotenv
load_dotenv()
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex, StorageContext
from llama_index.core .node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from retrieval.vector_store import (get_all_document_ids,get_vector_store, document_exists, get_document_hash, delete_document)
from llama_index.readers.docling import DoclingReader
from llama_index.readers.file import (PyMuPDFReader, DocxReader, PptxReader, HTMLTagReader,MarkdownReader,FlatReader)
import hashlib

from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR= BASE_DIR / 'data'

Settings.text_splitter = SentenceSplitter(
    chunk_size=configs.chunk_size,
    chunk_overlap=configs.chunk_overlap
)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    embed_batch_size=1,
    device="cpu"
)


# Validate the size of files in the data directory
def validate_size(file_path: Path):

    size = file_path.stat().st_size

    if size > configs.max_file_size:
        raise ValueError(
            f"{file_path.name} exceeds 10 MB"
        )

# Validate the encoding of text files in the data directory
def validate_encoding(file_path: Path):

    if file_path.suffix.lower() in [".txt", ".md"]:

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:
                f.read()

        except UnicodeDecodeError:

            raise ValueError(
                f"{file_path} is not UTF-8 encoded"
            )

# Create metadata for a given file path
def create_metadata(file_path: Path):
    file_path = Path(file_path)

    return {
        "source_document_id": str(file_path),
        "source_path": str(file_path),
        "title": file_path.stem,
        "last_modified":
            datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat(),
        "doc_type":
            file_path.suffix.lower(),
        "file_hash":
            get_content_hash(file_path)
    }

def get_content_hash(file_path: Path) -> str:
    return hashlib.sha256(
                file_path.read_bytes()
            ).hexdigest()

def get_page_number(doc):
    page = (
        doc.metadata.get("page_label") 
        or doc.metadata.get("source") 
        or doc.metadata.get("page_number")
        or doc.metadata.get("page")
    )
    
    if page is not None:
        return str(page)
    else:
        return "N/A"

def load_document(file_path: Path):
    reader = SimpleDirectoryReader(input_files=[str(file_path)],
    recursive=True,
    file_extractor=file_extractor, 
    file_metadata=create_metadata)

    return reader.load_data()

docling_reader = DoclingReader()
pdf_reader = PyMuPDFReader()
docx_reader = DocxReader()
pptx_reader = PptxReader()
html_reader = HTMLTagReader()
md_reader = MarkdownReader()
txt_reader = FlatReader()

file_extractor = {
    ".pdf": pdf_reader,
    ".docx": docx_reader,
    ".pptx": pptx_reader,
    ".html": html_reader,
    ".md": md_reader,
    ".txt": txt_reader,
    ".asciidoc": docling_reader,
}

#load documents from the data directory and validate them
documents_to_index = []
current_documents_ids = []
for file in DATA_DIR.rglob("*"):

    if not file.is_file():
        continue

    validate_size(file)
    validate_encoding(file)
    metadata = create_metadata(file)
    document_id = metadata["source_document_id"]
    current_documents_ids.append(document_id)

    if document_exists(document_id):
        existing_hash = get_document_hash(document_id)
        current_hash = get_content_hash(file)
        
        if existing_hash != current_hash:
            print(f"Document {metadata.get('title')} has changed. Updating...")
            delete_document(document_id)
            documents=load_document(file)
            for document in documents:
                document.metadata["page_number"] = get_page_number(document)
            documents_to_index.extend(documents)
        else:
            print(f"Document {metadata.get('title')} is unchanged. Skipping...")
            continue
    else:
        print(f"New document: {metadata.get('title')}. Adding to index...")
        documents=load_document(file)
        for document in documents:
            document.metadata["page_number"] = get_page_number(document)
        documents_to_index.extend(documents)

if configs.sync_delete:
    existing_document_ids = get_all_document_ids()
    current_documents_ids = tuple(current_documents_ids)
    for doc_id in existing_document_ids:
        if doc_id not in current_documents_ids:
            print(f"Document {doc_id} no longer exists. Deleting...")
            delete_document(doc_id)

# if documents_to_index:
#     print(f"Extending index with {len(documents_to_index)} documents...")
#     vector_store = get_vector_store()
#     storage_context = StorageContext.from_defaults(vector_store=vector_store)
#     index = VectorStoreIndex.from_documents(
#         documents_to_index,
#         storage_context=storage_context
#     )

if documents_to_index:
    print(f"Extending index with {len(documents_to_index)} documents...")
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    for document in documents_to_index:
        VectorStoreIndex.from_documents(
            [document],
            storage_context=storage_context
        )