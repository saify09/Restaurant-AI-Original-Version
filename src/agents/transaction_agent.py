import os
from smolagents import CodeAgent, InferenceClientModel
from src.tools.transaction_tools import CreateOrderTool, GetOrderStatusTool, RefundRequestTool
from src.utils.state_manager import StateManager

def create_transaction_agent(state_manager: StateManager):
    token = os.getenv("HF_TOKEN")
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-0.5B-Instruct", token=token)
    
    tools = [
        CreateOrderTool(state_manager),
        GetOrderStatusTool(state_manager),
        RefundRequestTool(state_manager)
    ]
    
    agent = CodeAgent(
        tools=tools,
        model=model,
        name="TransactionAgent",
        description="Order manager. RULES: 1. ONLY use create_order, get_order_status, or request_refund. 2. NEVER refund without ComplianceApproval: True. 3. Use final_answer() to finish.",
        max_steps=5
    )
    
    return agent
