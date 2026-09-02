""" comparing all variants of the prompts against all of our ticket fictures to compare results """

from ticket_assistant.converse import converse, text_of, usage_of, format_user_message
from ticket_assistant.fixtures import VALID_PRIORITIES, format_tickets
from ticket_assistant.prompts import PROMPT_VARIANTS


def _normalize(raw: str) -> str:
    """ normalize a response to one of three labels or "unparseable" """

    # removing any extra characters we think we might get back from the model
    # "High."
    cleaned = raw.strip().lower().strip(".!\"' \n")
    if cleaned in VALID_PRIORITIES:
        return cleaned

    # Fall back is to check for the first valid label in the response 
    # clean out these: high: / high, / high;
    for word in cleaned.replace(":", " ").replace(";", " ").replace(",", " "):
        word = word.strip(".!\"' \n")
        if word in VALID_PRIORITIES:
            return word
    return "unparseable"


def evaluate_variant(name: str, system_prompt: str, tickets: list[dict]) -> dict:
    """ run a system prompt against all ticket fixtures and record results """

    correct = 0
    misses = []
    input_tokens = 0
    output_tokens = 0
    loose_output = 0

    for ticket in tickets:
        response = converse(
            [format_user_message(f"Ticket:\n{ticket["text"]}")],
            system=system_prompt,
            max_tokens=64,
            temperature=0.0     # we want DETERMINISTIC results for evaluations
        )

        usage = usage_of(response)
        input_tokens += usage["input_tokens"]
        output_tokens += usage["output_tokens"]

        raw = text_of(response)
        predicted = _normalize(raw)

        # track the number of times the variant creates a prompt that NEEDED to be normalized
        if raw not in VALID_PRIORITIES:
            loose_output += 1

        # track correct responses
        if predicted == ticket["expected"]:
            correct += 1
        else:
            misses.append({
                "id": ticket["id"], 
                "expected": ticket["expected"], 
                "predicted": predicted
            })

    return {
        "name": name,
        "correct": correct,
        "total": len(tickets),
        "accuracy": correct / len(tickets),
        "avg_input_tokens": input_tokens / len(tickets),
        "avg_output_tokens": output_tokens / len(tickets),
        "loose_output": loose_output,
        "misses": misses
    }


if __name__ == "__main__":
    tickets = format_tickets()
    results = []

    for name, prompt in PROMPT_VARIANTS.items():
        print("Running Variant: " + name)
        results.append(evaluate_variant(name, prompt, tickets))


    for result in results:
        print(f"--- {result["name"]} ---")
        print(f"\tcorrect: {result["correct"]}/{result["total"]}")
        print(f"\taccuracy: {result["accuracy"]}")
        print(f"\tavg. input: {result["avg_input_tokens"]}")
        print(f"\tavg. output: {result["avg_output_tokens"]}")
        print(f"\tloose output: {result["loose_output"]}")

        for miss in result["misses"]:
            print(f"\tmiss: {miss["id"]}")
            print(f"\t\texpected: {miss["expected"]}")
            print(f"\t\tpredicted: {miss["predicted"]}")
