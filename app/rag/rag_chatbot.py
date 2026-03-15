import pickle
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
load_dotenv()


# Load chunks for BM25
with open("filtered_chunks.pkl", "rb") as f:
    filtered_chunks = pickle.load(f)
print(f"✅ Loaded {len(filtered_chunks)} chunks")

# Reconnect embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# Reconnect Qdrant
client = QdrantClient(host="localhost", port=6333)
vector_store = QdrantVectorStore(
    client=client,
    collection_name="kumbh_rag_semantic",
    embedding=embeddings
)

# Dense Retriever
qdrant_retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 10,
    }
)

#Sparse Retriever
from langchain_community.retrievers import BM25Retriever
bm25_retriever = BM25Retriever.from_documents(filtered_chunks)
bm25_retriever.k = 6

from langchain_classic.retrievers import EnsembleRetriever
hybrid_retriever = EnsembleRetriever(
    retrievers=[qdrant_retriever, bm25_retriever],
    weights=[0.6, 0.4]
)

# Load cross-encoder model for second-stage reranking
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_docs(query, docs):

    pairs = [(query, doc.page_content) for doc in docs]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

    return [doc for doc, _ in ranked[:5]]

from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-8b-instant",temperature=0.2)

from langchain_core.prompts import ChatPromptTemplate

query_expansion_prompt = ChatPromptTemplate.from_template(
"""
You are a search query optimizer for a RAG system about Nashik Kumbh Mela.

Rewrite the user's question so that it is clearer and contains useful keywords
for retrieving relevant documents.

Return ONLY the improved query.

User Question:
{question}

Improved Query:
"""
)

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

query_expansion_chain = (
    {
        "question": RunnablePassthrough()
    }
    | query_expansion_prompt
    | llm
    | StrOutputParser()
    
)

def enhance_query(question):
    
    improved_query = query_expansion_chain.invoke({"question": question})
    
    print("Original Query:", question)
    print("Enhanced Query:", improved_query)
    
    return improved_query

def retrieve_docs(question):

    enhanced_query = enhance_query(question)

    docs = hybrid_retriever.invoke(enhanced_query)

    # remove duplicates
    unique_docs = {doc.page_content: doc for doc in docs}.values()

    docs = rerank_docs(enhanced_query, list(unique_docs))

    return docs

def format_docs(docs):
    return "\n\n".join(
        f"[Category: {doc.metadata.get('category')}]\n{doc.page_content}"
        for doc in docs
    )

from langchain_core.prompts import ChatPromptTemplate

answer_prompt = ChatPromptTemplate.from_template(
"""
You are an assistant answering questions about Nashik Kumbh Mela.

Use only the provided context to answer the question.

Guidelines:
- If the answer is not in the context, say:
  "I could not find this information in the documents."
- Keep the answer concise.
- If possible, mention the source category.

Context:
{context}

Question:
{question}

Answer:
"""
)

from langchain_core.runnables import RunnableLambda,RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

enhanced_chain = (
    {
        "context":RunnableLambda(retrieve_docs) | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | answer_prompt
    | llm
    | StrOutputParser()
)