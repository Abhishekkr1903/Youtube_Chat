
# ================================
# 1. IMPORTS & SETUP
# ================================
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

# Custom LLM loader (your file)
from llm.model import get_llm

# Load environment variables
load_dotenv()


# ================================
# 2. FETCH YOUTUBE TRANSCRIPT
# ================================
video_id = "UabBYexBD4k"  # Only video ID

try:
    api = YouTubeTranscriptApi()

    # Fetch transcript in English
    transcript_data = api.fetch(video_id, languages=["en"])

    # Convert transcript objects → plain text
    transcript = " ".join([item.text for item in transcript_data])

except TranscriptsDisabled:
    print("No captions available for this video.")

# print(transcript_data[:500])  # Print first 500 chars of transcript for sanity check
# print(transcript[:20])

# ================================
# 3. SPLIT TEXT INTO CHUNKS
# ================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Convert text → LangChain Document objects
chunks = splitter.create_documents([transcript])

# print(f"Number of chunks: {len(chunks)}")
# print(chunks[1])


# ================================
# 4. EMBEDDINGS + VECTOR STORE
# ================================
# Using HuggingFace embeddings (local, no API issues)

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# Create FAISS vector database
vector_store = FAISS.from_documents(chunks, embeddings)

# print(vector_store.index_to_docstore_id)


# ================================
# 5. RETRIEVER
# ================================
# Converts vector DB → retriever (search interface)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# Example (manual testing)
# docs = retriever.invoke("What is the video about?")
# for doc in docs:
#     print(doc.page_content)
#     print("-" * 50)


# ================================
# 6. LOAD LLM
# ================================
model = get_llm()


# ==========================================================
# 7. (OPTIONAL) WITHOUT CHAINS - MANUAL RAG PIPELINE
# ==========================================================
"""
# Step 1: Ask question
question = "Is LLM discussed in this video?"

# Step 2: Retrieve relevant chunks
retrieved_docs = retriever.invoke(question)

# Step 3: Convert docs → context string
context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

# Step 4: Create prompt manually
prompt = PromptTemplate.from_template(\"\"\"
You are a helpful assistant.
Answer ONLY from the provided transcript context.
If context is insufficient, say "I don't know".

Context:
{context}

Question:
{question}
\"\"\")

final_prompt = prompt.invoke({
    "context": context_text,
    "question": question
})

# Step 5: Generate answer
answer = model.invoke(final_prompt)

print(answer.content)
"""


# ==========================================================
# 8. WITH CHAINS (LCEL) - CLEAN PIPELINE
# ==========================================================

# Helper: Convert retrieved docs → single string
def format_docs(retrieved_docs):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)


# Prompt template
prompt = PromptTemplate.from_template("""
You are a helpful assistant.
Answer ONLY from the provided transcript context.
If context is insufficient, say "I don't know".

Context:
{context}

Question:
{question}
""")


# Parallel chain:
# - Extract question → send to retriever → format context
# - Pass question forward
parallel_chain = RunnableParallel({
    "context": RunnableLambda(lambda x: x["question"]) | retriever | RunnableLambda(format_docs),
    "question": RunnablePassthrough()
})


# Output parser (convert model output → string)
parser = StrOutputParser()


# Final pipeline:
# input → parallel → prompt → model → parser
final_chain = parallel_chain | prompt | model | parser


# ================================
# 9. RUN QUERY
# ================================
# question = "Summarise me this video"

# answer = final_chain.invoke({
#     "question": question
# })

# print(answer)

#===============================
# Changes for stremlit app
#===============================
def ask_question(question: str):
    return final_chain.invoke({
        "question": question
    })
