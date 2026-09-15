from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

from oncall.llm import get_chat_model
from typing import cast


ALARM = (
    "ALARM checkout-api-5xx-rate in ALARM at 14:02 UTC. "
    "5xx ratio moved 0.2% -> 96.4% over 3 minutes. Deployment d-8814 "
    "completed at 13:59 UTC."
)


############################
### configure the prompt ###
############################
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an on-call triage support assistant. Answer in one sentence."),
        ("human", "{alert}")
    ]
)

parser = StrOutputParser()      # take in a AIMessage and give you just a string out

# because this is a runnable, we can invoke the prompt alone - without a model and without cost (no response will be given)
for message in prompt.invoke({"alert": ALARM}).to_messages():
    print(parser.invoke(message))


#########################
### compose the chain ###
#########################
model = get_chat_model()

chain = prompt | model | parser

print("\n=== INSIDE THE CHAIN ===")
print("\t type: " + type(chain).__name__)                               # the type of the chain
sequence = cast(RunnableSequence, chain)
print("\t steps: ", [type(step).__name__ for step in sequence.steps])   # the steps within the chain
print("\t wants: ", chain.get_input_jsonschema().get("required"))       # required properties for the chain to run


#########################
### execute the chain ###
#########################

print("\n=== RESULT OF CHAIN ===")
print("=== invoke ===")
print(chain.invoke({"alert": ALARM}))       # one line of code to invoke all 3 steps

print("=== stream ===")
for chunk in chain.stream({"alert": ALARM}):
    print(chunk)

print("=== batch ===")
more_alerts = [
    {"alert": ALARM},
    {"alert": "ALARM orders-db-cpu at 98% for 11 minutes, replica lag 40s."},
    {"alert": "ALARM nightly-reconciliation took 51m against a p50 of 12m."},
]
for i, output in enumerate(chain.batch(more_alerts, config={"max_concurrency": 3})):
    print(f"{i}: {output}")


#####################
### chain-ception ###
#####################

shorten = ChatPromptTemplate.from_messages(
    [("human", "Rewrite this in under 8 words, no punctuation.\n\n{text}")]
)

# whatever chain produces, set that as the "text" properrty `shorten` expects
nested_chain = {"text" : chain} | shorten | model | parser

print("\n=== CHAIN-CEPTION ===")
print(nested_chain.invoke({"alert": ALARM}))  