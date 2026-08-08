from generation.models import Chunk
from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT="""
You are a helpful assistant that answers questions using only the provided context.

Rules:
1. Answer only using information from the provided context.
2. Cite every factual claim using the provided citation format.
3. If the context does not contain enough information to answer the question, say that you don't know.
4. Do not invent or assume information that is not present in the context.
"""

def format_context(chunks: list[Chunk]):
    context=""""""
    for n,chunk in enumerate(chunks):
        source = chunk.source
        page = chunk.metadata.get("page_number")
        content = chunk.text
        text=f"""[{n+1}]
Source: {source}
Page: {page}
Content: 
{content}
"""
        context+= text
    return context

def build_prompt(question: str, retrieved_chunks: list[Chunk]):
    context = format_context(retrieved_chunks)
    prompt= f"""
CONTEXT:
{context}

USER QUESTION:
{question}
"""
    return prompt

def build_prompt_template()-> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
        ("system", SYSTEM_PROMPT),
        ("human", """
CONTEXT:
{context}

USER QUESTION:
{question}

Answer the question using only the provided context. Cite sources as [<source number>]""")
        ]
    )

def prompt_inputs(question: str, context: list[Chunk]) -> dict:
    return {
        "context": format_context(context),
        "question": question
    }
