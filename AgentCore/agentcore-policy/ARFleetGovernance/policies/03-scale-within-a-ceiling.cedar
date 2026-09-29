// allow scaling as long as the replica value isn't too high and we aren't in prod

permit(
    principal, 
    action == AgentCore::Action::"ARFleetTools___scale_service",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:397345411365:gateway/arfleetgovernance-arfleetgateway-nri1sfljea"
)
when {

    // context.input is looking at payload of request sent to the gateway
    context.input has environment && 
    context.input has replicas && 
    context.input.environment != "prod" &&
    context.input.replicas <= 10
};