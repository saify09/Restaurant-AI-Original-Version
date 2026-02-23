from smolagents import CodeAgent, InferenceClientModel
from src.tools.compliance_tools import PolicyLookupTool, VerifyComplianceTool
from src.utils.rag_pipeline import RAGPipeline

def create_compliance_agent(rag_pipeline: RAGPipeline):
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-0.5B-Instruct")
    
    tools = [
        PolicyLookupTool(rag_pipeline),
        VerifyComplianceTool(rag_pipeline)
    ]
    
    agent = CodeAgent(
        tools=tools,
        model=model,
        name="ComplianceAgent",
        description="Policy expert. RULES: 1. ONLY use policy_lookup or verify_compliance. 2. Return 'ComplianceApproval: True' or 'False'. 3. DO NOT hallucinate tools. 4. Use final_answer() to finish.",
        max_steps=5
    )
    
    return agent
