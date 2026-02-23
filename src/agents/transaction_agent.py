import os
from smolagents import CodeAgent, InferenceClientModel
from src.tools.transaction_tools import CreateOrderTool, GetOrderStatusTool, RefundRequestTool
from src.utils.state_manager import StateManager

def create_transaction_agent(state_manager: StateManager):
    token = os.getenv("HF_TOKEN")
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-1.5B-Instruct", token=token)
    
    tools = [
        CreateOrderTool(state_manager),
        GetOrderStatusTool(state_manager),
        RefundRequestTool(state_manager)
    ]
    
    agent = CodeAgent(
        tools=tools,
        model=model,
        name="TransactionAgent",
        description="Order manager. Can create orders, check status, and process refunds.",
        max_steps=5
    )
    
    return agent
