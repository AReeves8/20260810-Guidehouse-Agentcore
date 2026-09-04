""" Retrieval-Augmented Generation over a Bedrock Knowledge Base. """

from ticket_assistant.aws import get_client, agent_runtime
from ticket_assistant.config import AWS_REGION, MODEL_ID, KNOWLEDGE_BASE_ID, KNOWLEDGE_BASE_TYPE
from ticket_assistant.converse import converse, text_of, format_user_message

# KB can either be managed or a vector store. These have different config properties
_SEARCH_CONFIG_KEY = (
    "managedSearchConfiguration" if KNOWLEDGE_BASE_TYPE == "managed" else "vectorSearchConfiguration"
)


GROUNDED_PROMPT = """You answer question's about our company's internal policies. 

Rules:
    1. Answer ONLY from the reference passages provided in the user message. 
    2. If the passages do not contain the answer, say exactly "The provided documents do not cover that." 
    Do not fall back on general knowledge. 
    3. Quote specific figures (days, percentages, prices) exactly as written.
    4. End your answer with a "Sources:" line naming the documents you used.
"""


# R - retrieve relevant chunks from KB
def retrieve(query: str, max_results: int = 4) -> list[dict]:
    """ returns up to 'max_results' number of chunks from KB that are relevant to 'query' """

    response = agent_runtime().retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={"text": query},

        # numberOfResults is a valid property for both managedSearchConfig and vectorSearchConfig
        retrievalConfiguration={_SEARCH_CONFIG_KEY: {"numberOfResults": max_results}}
    )

    return [
        {
            "score": round(result.get("score", 0.0), 4),
            "text": result["content"]["text"],
            "source": result.get("location", {}).get("s3Location", {}).get("uri", "[UNKNOWN SOURCE]")
        }
        for result in response.get("retrievalResults", [])
    ]

# A - augment the user's prompt to include any found chunks
def build_grounded_prompt(query: str, chunks: list[dict]) -> str:
    """ adding any found chunks to the user's query """

    # check if there are any chunks to add
    if not chunks:
        return f"No refernce passages were found for this question.\n\n---\n\nQuestion: {query}"

    # passages before question to ground the model before asking a question
    return "Reference Passages:".join(
        f"\n\n[Passage {i} from {chunk["source"]}]\n{chunk["text"]}"
        for i, chunk in enumerate(chunks, start=1)
    )


# G - prompt the model with the freshly retreived passages
def answer_with_sources(query: str, max_results: int = 4) -> dict:
    """ calls retreive and augent steps before sending prompt to model 
    
        with a managed KB, we have to manually do each one of the steps
            with a vectored KB, there is a 'RetrieveAndGenerate' function from Boto3 that does it all at once
    """

    chunks = retrieve(query, max_results)
    user_message = [format_user_message(build_grounded_prompt(query, chunks))]

    response = converse(
        user_message, 
        system=GROUNDED_PROMPT,
        max_tokens=500,
        temperature=0.0
    )

    return {
        "answer": text_of(response),
        "sources": [chunk["source"] for chunk in chunks],
        "chunks": chunks        # useful for debugging to see what chunks were used and what they look like
    }


if __name__ == "__main__":

    questions = [
        "How long does a customer have to return an item, and is there a fee?",
        "Does the Standard plan include SSO?",
        "Do unused seats roll over to the next month?",
        "A customer's saved-card checkout failed. Is there a known issue, and "
        "does it qualify for a restocking-fee waiver?",
    ]

    for q in questions:
        result = answer_with_sources(q)

        print("Question: " + q)
        print(f"Answer: {result["answer"]}")
        for source in result["sources"]:
            print(f"\t{source}")