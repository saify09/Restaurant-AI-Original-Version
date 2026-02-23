import os
from smolagents import CodeAgent, InferenceClientModel
from src.tools.compliance_tools import PolicyLookupTool, VerifyComplianceTool
from src.utils.rag_pipeline import RAGPipeline

def create_compliance_agent(rag_pipeline: RAGPipeline):
    token = os.getenv("HF_TOKEN")
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-1.5B-Instruct", token=token)
    
    tools = [
        PolicyLookupTool(rag_pipeline),
        VerifyComplianceTool(rag_pipeline)
    ]
    
    agent = CodeAgent(
        tools=tools,
        model=model,
        name="ComplianceAgent",
        description="Policy expert. Verifies if requests like refunds or cancellations comply with restaurant rules.",
        max_steps=5
    )
    
    return agent
