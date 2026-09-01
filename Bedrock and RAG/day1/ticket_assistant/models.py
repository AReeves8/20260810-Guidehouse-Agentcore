""" 
    use the bedrock control plane to find the models we have access to 

        - filter models to find the ones we can use:
            - non-legacy models
            - text input and text ouput
            - on-demand models
"""

from ticket_assistant.aws import bedrock_control

def _catalog() -> dict[str, dict]:
    """ every model in our region """
    response = bedrock_control().list_foundation_models()
    return {summary["modelId"]: summary for summary in response["modelSummaries"]}

def _is_text_chat_and_non_legacy(summary: dict) -> bool:
    """ check for text input and output AND check if it is legacy or not """

    # checks if text is a possible input mode
    if "TEXT" not in summary.get("inputModalities", []):
        return False

    # checks if text is a possible output mode
    if "TEXT" not in summary.get("outputModalities", []):
        return False

    # checks if the model is not in the 'legacy' stage of the lifecycle
    return summary.get("modelLifecycle", {}).get("status") != "LEGACY"


def callable_models(provider: str | None = None) -> list[dict]:
    """ all the models we can work with in this app """

    rows = []
    for model_id, summary in _catalog().items():

        # disregard models that are legacy or non-text
        if not _is_text_chat_and_non_legacy(summary):
            continue

        # filter for a specific provider
        if provider and summary.get("providerName", "").lower() != provider.lower():
            continue

        # getting the inference types of the model
        inference_types = summary.get("inferenceTypesSupported", [])

        rows.append(
            {
                "model_id": model_id,
                "provider": summary.get("providerName", "???"),
                "name": summary.get("modelName", "???"),

                # can still call models that aren't on-deman, but takes some extra steps
                "is_on_demand": "ON_DEMAND" in inference_types
            }
        )

    return rows


if __name__ == "__main__":
    print("--- TEXT/CHAT MODELS WE CAN CALL ON DEMAND ---")
    on_demand_models = [m for m in callable_models() if m["is_on_demand"]]
    for model in on_demand_models:
        print(f"{model["model_id"]:<45} : {model["provider"]}")

    print("\n--- TEXT/CHAT MODELS WE CAN CALL WITH PROFILE ACCESS ---")
    profile_models = [m for m in callable_models() if not m["is_on_demand"]]
    for model in profile_models:
        print(f"{model["model_id"]:<45} : {model["provider"]}")
