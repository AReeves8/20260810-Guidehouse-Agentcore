// allow prod restarts when the user is a Fleet Operator in IAM

permit(
    principal is AgentCore::IamEntity, 
    action == AgentCore::Action::"ARFleetTools___restart_service",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:397345411365:gateway/arfleetgovernance-arfleetgateway-nri1sfljea"
)
when {
    context.input has environment && 
    context.input.environment == "prod" &&
    principal.id like "arn:aws:sts::*:assumed-role/*FleetOperator"
};