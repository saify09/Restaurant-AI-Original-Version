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
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-1.5B-Instruct", token=token) 
    
    manager = CodeAgent(
        tools=[AuditTool(state_manager)],
        model=model,
        managed_agents=[compliance_agent, transaction_agent, menu_agent],
        name="ManagerAgent",
        description="""Central orchestrator for GourmetAI. 
        You are the CEO/Manager. You DO NOT have the tools to lookup menus, manage orders, or check policies yourself.
        You MUST delegate to your specialist agents.
        
        AGENTS AVAILABLE:
        - compliance_agent: Use for policy checks, T&C verification, and refund approvals.
        - transaction_agent: Use for creating orders, checking status, and processing refunds.
        - menu_agent: Use for menu lookups and item availability.
        
        RULES:
        1. NEVER define your own functions or placeholder logic.
        2. NEVER call sub-tools like 'menu_lookup' directly. Use menu_agent(task='...').
        3. ALWAYS delegate to specialized agents.
        
        FEW-SHOT EXAMPLES:
        User: "What is on the menu?"
        Action: menu_agent(task="What items are available on the menu today?")
        
        User: "Status of order 123?"
        Action: transaction_agent(task="Get the status for order 123")
        
        User: "I want a refund for order 456"
        Action: 
            step1 = compliance_agent(task="Can order 456 be refunded per policy?")
            if "ComplianceApproval: True" in step1:
                transaction_agent(task="Process refund for order 456")
            audit_log(user_id=user_id, action="REFUND_PROCESSED", reasoning=step1, risk_level="LOW")
        
        IMPORTANT: Use final_answer("your summary to the user") to finish.
        """,
        max_steps=12,
        additional_authorized_imports=['pandas', 'json', 'time', 'datetime']
    )
    
    return manager, state_manager, rag_pipeline
