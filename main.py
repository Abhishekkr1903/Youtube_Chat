from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate

# Add your code here that uses these imports, e.g.:
# transcript = YouTubeTranscriptApi.get_transcript("video_id")
# ... etc.
from dotenv import load_dotenv
import os

from llm.model import get_llm

load_dotenv()

video_id = "UabBYexBD4k" # only the ID, not full URL
try:
    # If you don’t care which language, this returns the “best” one

    # transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])

    # # Flatten it to plain text
    # transcript = " ".join(chunk["text"] for chunk in transcript_list)
    # print(transcript)
    api = YouTubeTranscriptApi()

    transcript_data = api.fetch(video_id,languages=["en"])

    transcript = " ".join([item.text for item in transcript_data])
    #print(transcript)

except TranscriptsDisabled:
    print("No captions available for this video.")

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])
#print(f"Number of chunks: {len(chunks)}")


#print(chunks[1])
from langchain_community.embeddings import HuggingFaceEmbeddings

# embeddings = HuggingFaceEmbeddings(
#     model_name="all-MiniLM-L6-v2"
# )
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")


from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vector_store = FAISS.from_documents(chunks, embeddings)

#print(vector_store.index_to_docstore_id)

#Retriver -> it is runnable

retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
#print(retriever)

#docs = retriever.invoke("What is the video about?")

# for doc in docs:
#     print(doc.page_content)
#     print("-" * 50)

#docs = retriever.invoke("What is LLM")
# print(docs[0].page_content)

#Augementation

from llm.model import get_llm
model=get_llm()


# prompt = PromptTemplate.from_template(
# template="""
# You are a helpful assistant.
# Answer ONLY from the provided transcript context.
# If the context is insufficient, just say you don't know.

# {context}
# Question: {question}

# input_variables|= ['context', 'question' ]
# """
# )

# question= "is the topic of LLM discussed in this video? if yes then what was discussed"
# retrieved_docs= retriever.invoke(question)

# context_text = "\n\n".join(doc.page_content for doc in retrieved_docs) # created function for this step in chains section, but for now we can do it here as well

# #final_prompt = prompt.invoke({"context": context_text, "question": question})

# Generation:

# answer = model.invoke(final_prompt)
#print(answer.content)


#Applying Chains

# from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
# from langchain_core.output_parsers import StrOutputParser

# def format_docs(retrieved_docs):
#     context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
#     return context_text

# parallel_chain = RunnableParallel
# ({
# 'context': retriever | RunnableLambda(format_docs),
# 'question': RunnablePassthrough()
# })

# parser=StrOutputParser()
# final_chain = parallel_chain |prompt | model | parser

# question = "is the topic of LLM discussed in this video? if yes then what was discussed"

# answer = final_chain.invoke({
#     "question": question
# })

# print(answer)

from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

def format_docs(retrieved_docs):
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text

prompt = PromptTemplate.from_template("""
You are a helpful assistant.
Answer ONLY from the provided transcript context.
If context is insufficient, say "I don't know".

Context:
{context}

Question:
{question}
""")

parallel_chain = RunnableParallel({
    "context": RunnableLambda(lambda x: x["question"]) | retriever | RunnableLambda(format_docs),
    "question": RunnablePassthrough()
})
parser = StrOutputParser()

final_chain = parallel_chain | prompt | model | parser

question = "is the topic of LLM discussed in this video? if yes then what was discussed"

answer = final_chain.invoke({
    "question": question
})

print(answer)