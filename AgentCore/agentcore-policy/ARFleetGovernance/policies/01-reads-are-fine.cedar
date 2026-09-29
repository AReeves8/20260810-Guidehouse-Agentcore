
// reading state of the fleet of services is not a problem, so allow all actions to it

permit(
    principal,

    // having multiple actions in one policy uses the 'in' keyword with a list
    action in [
        AgentCore::Action::"ARFleetTools___get_service_status",
        AgentCore::Action::"ARFleetTools___read_metrics",
    ],
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:397345411365:gateway/arfleetgovernance-arfleetgateway-nri1sfljea"
);