from langchain_openrouter import ChatOpenRouter
from langchain_core.output_parsers import StrOutputParser
from retrieval.retriever import Retriever
from generation.prompt import prompt_inputs, build_prompt_template
from generation.citations import extract_citations

from config import configs

def get_llm() -> ChatOpenRouter:
    model = ChatOpenRouter(
        model=configs.llm_model,
        api_key=configs.or_api_key,
        max_tokens=configs.max_tokens,
        temperature=configs.temperature,
        retries=2
        )
    return model

retriever = Retriever()
prompt = build_prompt_template()
llm = get_llm()
parser = StrOutputParser()
chain = prompt | llm | parser

def answer_question(question, top_k = configs.top_k_m):
    chunks = retriever.retrieve_chunks(query=question,top_k=top_k)
    inputs = prompt_inputs(question=question, context=chunks)
    answer = chain.invoke(inputs)
    return extract_citations(answer, chunks)




    






