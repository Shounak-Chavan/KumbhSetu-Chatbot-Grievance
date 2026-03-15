from langchain_core.documents import Document
import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

# Load documents from the specified directory

dir_loader = DirectoryLoader(
    path = "../dataset/kumbh_rag_dataset",
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
    show_progress=True
)

documents = dir_loader.load()
print(f"Number of documents loaded: {len(documents)}")

# Added Custom Metadata

# For Custom Metadata Extraction

for doc in documents:
    
    # Get file path
    path = doc.metadata["source"]
    
    # Extract folder and filename
    parts = path.replace("\\","/").split("/")
    category = parts[-2]        # folder name
    doc_name = parts[-1]        # file name

    text = doc.page_content
    
    source_link = None

    # Extract SOURCE link if present
    if text.startswith("SOURCE:"):
        first_line, rest = text.split("\n", 1)
        source_link = first_line.replace("SOURCE:", "").strip()
        doc.page_content = rest.strip()

    # Update metadata
    doc.metadata = {
        "category": category,
        "doc_name": doc_name,
        "source_link": source_link
    }

# Embeding + Semantic Chunking

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # ← model_name not model
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}  # ← important for cosine similarity
)

from langchain_experimental.text_splitter import SemanticChunker
chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=85
)

sem_chunks = chunker.split_documents(documents)
print(len(sem_chunks))

from langchain_text_splitters import RecursiveCharacterTextSplitter
rec_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "। ", ". ", " ", ""]  # added । for Hindi text
    )

final_chunks = []

for chunk in sem_chunks:
    
    if len(chunk.page_content) > 1000:
        sub_chunks = rec_splitter.split_documents([chunk])
        final_chunks.extend(sub_chunks)
        
    else:
        final_chunks.append(chunk)

print("Final chunks:", len(final_chunks))

filtered_chunks = [
    chunk for chunk in final_chunks
    if len(chunk.page_content.strip()) > 120
]
print("Filtered chunks:", len(filtered_chunks))

import pickle
with open("filtered_chunks.pkl", "wb") as f:
    pickle.dump(filtered_chunks, f)
print("✅ Chunks saved")

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)

# Add this before create_collection
if client.collection_exists("kumbh_rag_semantic"):
    client.delete_collection("kumbh_rag_semantic")
    print("🗑️ Deleted old collection")

if not client.collection_exists("kumbh_rag_semantic"):
    client.create_collection(
        collection_name="kumbh_rag_semantic",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )
    print("✅ Collection created")
else:
    print("✅ Collection already exists")

from langchain_qdrant import QdrantVectorStore

vector_store = QdrantVectorStore(
    client=client,
    collection_name="kumbh_rag_semantic",
    embedding=embeddings
)

vector_store.add_documents(filtered_chunks)
print(f"✅ {len(filtered_chunks)} chunks stored in Qdrant")