import os
from smolagents import CodeAgent, InferenceClientModel
from src.tools.menu_tools import MenuLookupTool
from src.utils.rag_pipeline import RAGPipeline

def create_menu_agent(rag_pipeline: RAGPipeline):
    token = os.getenv("HF_TOKEN")
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-1.5B-Instruct", token=token)
    
    tools = [
        MenuLookupTool(rag_pipeline)
    ]
    
    agent = CodeAgent(
        tools=tools,
        model=model,
        name="MenuAgent",
        description="Menu expert. RULES: 1. ONLY use menu_lookup. 2. DO NOT hallucinate web tools. 3. Use final_answer() to finish.",
        max_steps=5
    )
    
    return agent
