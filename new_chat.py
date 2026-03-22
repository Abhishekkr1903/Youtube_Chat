
# ================================
# BUILD PIPELINE FUNCTION (DYNAMIC VIDEO)
# ================================

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model import get_llm


def build_chain(video_id: str):
    # -------- Fetch transcript --------
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id, languages=["en"])
        transcript = " ".join([item.text for item in transcript_data])
    except TranscriptsDisabled:
        return None

    # -------- Split --------
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])

    # -------- Embeddings --------
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # -------- LLM --------
    model = get_llm()

    # -------- Prompt --------
    prompt = PromptTemplate.from_template("""
    You are a helpful assistant.
    Answer ONLY from the provided transcript context.
    If context is insufficient, say "I don't know".

    Context:
    {context}

    Question:
    {question}
    """)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    parallel_chain = RunnableParallel({
        "context": RunnableLambda(lambda x: x["question"]) 
                   | retriever 
                   | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })

    parser = StrOutputParser()
    final_chain = parallel_chain | prompt | model | parser

    return final_chain


# ================================
# ASK FUNCTION
# ================================
def ask_question(chain, question: str):
    return chain.invoke({"question": question})

