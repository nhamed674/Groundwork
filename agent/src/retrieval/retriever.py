import os
from llama_index.core import SimpleDirectoryReader
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR= BASE_DIR / 'data'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Validate the size of files in the data directory
def validate_size(file_path: Path):

    size = file_path.stat().st_size

    if size > MAX_FILE_SIZE:
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

    return {

        "source_path": str(file_path),

        "title": file_path.stem,

        "last_modified":
            datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat(),

        "doc_type":
            file_path.suffix.lower()
    }

#load documents from the data directory and validate them
for file in DATA_DIR.rglob("*"):

    if not file.is_file():
        continue

    validate_size(file)
    validate_encoding(file)
    loaded_docs = SimpleDirectoryReader(input_files=[str(file)]).load_data()

reader = SimpleDirectoryReader(
    input_dir=str(DATA_DIR),
    recursive=True, 
    file_metadata=create_metadata
)

documents = reader.load_data()

print(
    f"Loaded {len(documents)} documents"
)
