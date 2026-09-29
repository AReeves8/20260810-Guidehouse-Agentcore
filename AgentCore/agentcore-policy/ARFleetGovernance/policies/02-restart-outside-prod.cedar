// we will allow the restart action, but only when the environment is not prod

permit(
    principal, 
    action == AgentCore::Action::"ARFleetTools___restart_service",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:397345411365:gateway/arfleetgovernance-arfleetgateway-nri1sfljea"
)
when {

    // context.input is looking at payload of request sent to the gateway
    context.input has environment && context.input.environment != "prod"
};