import os
from smolagents import CodeAgent, InferenceClientModel
from src.agents.compliance_agent import create_compliance_agent
from src.agents.transaction_agent import create_transaction_agent
from src.agents.menu_agent import create_menu_agent
from src.tools.audit_tools import AuditTool
from src.utils.state_manager import StateManager
from src.utils.rag_pipeline import RAGPipeline

def create_manager_agent():
    # Initialize Core Components
    state_manager = StateManager()
    rag_pipeline = RAGPipeline()
    
    # Initialize Specialized Agents
    compliance_agent = create_compliance_agent(rag_pipeline)
    transaction_agent = create_transaction_agent(state_manager)
    menu_agent = create_menu_agent(rag_pipeline)
    
    # Top-level Orchestrator
    token = os.getenv("HF_TOKEN")
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-7B-Instruct", token=token) 
    
    manager = CodeAgent(
        tools=[AuditTool(state_manager)],
        model=model,
        managed_agents=[compliance_agent, transaction_agent, menu_agent],
        name="ManagerAgent",
        description="""Central orchestrator for GourmetAI. 
        You are the CEO. You DO NOT have tools for menus, orders, or policies.
        You MUST delegate every specialized task to your agents.
        
        - menu_agent: For ANY menu or food lookup.
        - transaction_agent: For orders, status checks, and refunds.
        - compliance_agent: For policy/rule verification (e.g., refund eligibility).
        
        RULES:
        1. NEVER write your own Python logic for tasks. Use the agents.
        2. NEVER call tools like 'menu_lookup' directly. Use menu_agent.
        3. For refunds: First call compliance_agent, then transaction_agent IF approved.
        
        Example:
        User: "What's on the menu?"
        Code: menu_agent(task="Get current menu items")
        """,
        max_steps=12,
        additional_authorized_imports=['pandas', 'json', 'time', 'datetime']
    )
    
    return manager, state_manager, rag_pipeline
