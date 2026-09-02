""" four different levels of prompts, each better than the last """


# no role, no definitions, no output contract. 
NAIVE = "Assign a priority to this support ticket."

# no definitions for what priorities mean
ROLE_AND_FORMAT = """You are a senior support engineer triaging incoming tickets.

Read the ticket and respond with exactly one word: low, medium, or high.
Output nothing else -- no explanation or punctuation.
"""

# provides definitions, but can take it further with examples...
WITH_RUBRIC = """You are a senior support engineer triaging incoming tickets.

Classify by BUSINESS IMPACT, not by how the customer sounds. 
A polite customer losing revenue outranks an angry customer with a cosmetic complaint.

    high    - revenue is being lost, data is exposed or corrupted, or a core workflow is unusable for customers right now.
    medium  - a real defect with a workaround or degraded performance that is costing time but not blocking work
    low     - cosmetic issues, feature requests, and questions

Output only one word: low, medium, or high. Output nothing else.
"""

# add ambiguous examples to help the model decide in uncertain scenarios
# don't use direct copies from your test samples as that would test memorization instead of generalization. 
# A technique called "Few Shot" - giving a model a small number of labeled examples
WITH_EXAMPLES = (
    WITH_RUBRIC + 
"""
EXAMPLES:

Ticket: "No huge rush, but our invoices have been generating with last month's totals since Friday. 
Accounting caught it before anything went out."
Prioity: high

Ticket: "THIS IS COMPLETELY UNACCEPTABLE!!!! Your logo is stretched on the login page and it looks terrible. 
FIX IT NOW."
Priority: low

Ticket: "The search results take about five seconds to come back since the update. It used to only take one."
Priority: medium
"""
)

PROMPT_VARIANTS = {
    "v1-naive": NAIVE,
    "v2-role": ROLE_AND_FORMAT,
    "v3-rubric": WITH_RUBRIC,
    "v4-examples": WITH_EXAMPLES
}