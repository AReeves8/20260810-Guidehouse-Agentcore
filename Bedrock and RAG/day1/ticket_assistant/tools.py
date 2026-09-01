""" 
    TOOLS
        - callouts to perform specific actions on behalf of your models
        - NOT EXECUTED BY THE MODEL
        - you tell the model what tools are available, what they're used for, how to use them, etc and the model decides when it needs them. 
            - you then EXECUTE the tool yourself and tell the model the result


        user -> system -> model -> tool call -> system -> model -> system -> user
            - tool loops where the model keeps requesting for tools to be used
                - program defensively to prevent this (max attempts)
                    - not restrict attempts for the entire conversation, but for subsequent tool calls on the same user prompt
"""

# sample data sets to use in place of external service or database
_ORDERS = {
    "A-1001": {"status": "delivered", "carrier": "UPS", "delivered_on": "2026-03-02"},
    "A-1002": {"status": "in_transit", "carrier": "FedEx", "expected_on": "2026-03-09"},
    "A-1003": {"status": "payment_failed", "reason": "card declined"},
}
_SERVICE_STATUS = {
    "checkout": "degraded -- saved-card payments failing since 2026-03-05",
    "search": "operational",
    "shipping": "operational",
}


def lookup_order_status(order_id: str) -> dict:
    """ tool call to find a specific order """
    return _ORDERS.get(order_id, {"error": f"No order with id {order_id}"})

def check_service_status(service: str) -> dict:
    """ tool call to check the status of a service """

    status = _SERVICE_STATUS.get(service.lower())

    if status is None:
        # if we receive an invlaid service, we will return the list of valid services. 
        return {"error": f"Unknown service: {service}", "known": sorted(_SERVICE_STATUS)}

    return {"service": service, "status": status}

# maps the function in python to a name we can give to the model
TOOL_FUNCTIONS = {
    "lookup_order_status": lookup_order_status,
    "check_service_status": check_service_status
}

# defining the tool config that can be passed to the model - requires a certain format
TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "lookup_order_status",

                # description is the ONLY thing telling the model when to use this tool. 
                # inadequate descriptions are the biggest reason for tool failures (tool misused or never called to begin with)
                "description": (
                    "Look up the current status of a customer order by its order ID. "
                    "Use when the customer mentions a specific order and you need to "
                    "know whether it shipped, was delivered, or failed payment."
                ),
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "Order ID in the form A-1234.",
                            }
                        },
                        "required": ["order_id"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "check_service_status",
                "description": (
                    "Check whether an internal service is currently healthy. "
                    "Use when a customer reports a failure that might be a known "
                    "outage rather than a problem with their own account."
                ),
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "service": {
                                "type": "string",
                                "description": "One of: checkout, search, shipping.",
                            }
                        },
                        "required": ["service"],
                    }
                },
            }
        },
    ]
}


def run_tool(tool_use: dict) -> dict:
    """ decides what tool to execute and returns the result of the tool """

    name = tool_use["name"]
    function = TOOL_FUNCTIONS.get(name)

    # if the function doesn't exist, tell the model that 
    if function is None:
        result, status = {"error": f"No such tool: {name}"}, "error"
    else:
        try:
            result, status = function(**tool_use["input"]), "success"
        except Exception as e:  
            """ handles the tool call failing for some reason """
            result, status = {"error": f"{type(e).__name__}: {e}"}, "error"

    return {
        "toolResult" : {

            # model will give a toolUseId and we need to tell the model that we completed that request by sending toolUseId back
            "toolUseId": tool_use["toolUseId"],
            "content": [{"json": result}],
            "status": status
        }
    }