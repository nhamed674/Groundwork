from generation.models import Citation, AgentResponse, Chunk
import re

def extract_citations(answer: str, chunks: list[Chunk]) -> AgentResponse:
    cited_ids = {int(num) for num in re.findall(r"\[(\d+)\]",answer)}
    valid_ids = set(range(1,len(chunks)+1))
    invalid_ids = cited_ids - valid_ids
    formatted_invalid_ids = ",".join(f"[{i}]" for i in invalid_ids)
    citation_warning = (f"Invalid citations found: {formatted_invalid_ids}. Max valid ID is {len(chunks)}."
        if invalid_ids else None)  
    valid_cited_ids = cited_ids & valid_ids


    citations = []
    for id in sorted(valid_cited_ids) : 
        citations.append(Citation(source_path=chunks[id-1].source_path,
                                  snippet=chunks[id-1].text[:300],
                                  source=chunks[id-1].source,
                                  page_number=chunks[id-1].metadata.get("page_number"),
                                  )
                        )
    
    return AgentResponse(answer=answer, 
                         citations=citations, 
                         citation_warning=citation_warning, 
                         invalid_citations=invalid_ids
                         )
    
    
