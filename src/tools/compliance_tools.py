from smolagents import Tool
from src.utils.rag_pipeline import RAGPipeline
from typing import Dict, Any, List

class PolicyLookupTool(Tool):
    name = "policy_lookup"
    description = "Search the legal documents (Privacy Policy, T&C) for compliance rules."
    inputs = {
        "query": {"type": "string", "description": "The compliance question or rule to look up"}
    }
    output_type = "string"

    def __init__(self, rag_pipeline: RAGPipeline, **kwargs):
        super().__init__(**kwargs)
        self.rag_pipeline = rag_pipeline

    def forward(self, query: str) -> str:
        results = self.rag_pipeline.query(query)
        if not results:
            return "No relevant policy found."
        
        formatted_results = "\n\n".join([f"Source: {r['source']}\nContent: {r['content']}" for r in results])
        return f"Found relevant policies:\n{formatted_results}"

class VerifyComplianceTool(Tool):
    name = "verify_compliance"
    description = "Verifies if an action is compliant with company policy."
    inputs = {
        "action": {"type": "string", "description": "The action to verify (e.g. 'REFUND', 'CANCELLATION')"},
        "context": {"type": "string", "description": "Context such as order age or reason"}
    }
    output_type = "string"

    def __init__(self, rag_pipeline: RAGPipeline, **kwargs):
        super().__init__(**kwargs)
        self.rag_pipeline = rag_pipeline

    def forward(self, action: str, context: str) -> str:
        query = f"Rules for {action}. Context: {context}"
        results = self.rag_pipeline.query(query)
        if not results:
            return "UNSURE: No policy found. Refusing by default."
            
        content = " ".join([r['content'] for r in results])
        return f"Policy Context: {content}\n\nDecision Requirement: MUST follow the rules mentioned in the content. If rules explicitly forbid the action, return DENIED."
