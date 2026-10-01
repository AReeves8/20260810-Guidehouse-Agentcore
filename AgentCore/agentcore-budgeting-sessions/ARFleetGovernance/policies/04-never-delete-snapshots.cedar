// never allow deleting of snapshots through the gateway

forbid(
    principal,
    action == AgentCore::Action::"ARFleetTools___delete_snapshot",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:397345411365:gateway/arfleetgovernance-arfleetgateway-nri1sfljea"
);