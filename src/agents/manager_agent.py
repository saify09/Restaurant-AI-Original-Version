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
        RULES:
        1. YOU ARE THE MANAGER. DO NOT perform specialized tasks yourself. 
        2. ALWAYS USE THE AGENTS: compliance_agent, transaction_agent, menu_agent.
        3. ERROR FIX: Do NOT call 'menu_lookup' directly. It belongs to menu_agent. Use menu_agent(task='lookup items').
        4. CRITICAL: Do NOT use forbidden functions like locals(), globals(), or any internal python guts.
        5. To call an agent, use: agent_name(task="specific request").
        6. ALWAYS call compliance_agent(task="...") before transaction_agent for refunds/cancellations.
        7. Use audit_log tool ONLY for final decisions (action, reasoning, risk).
        8. To finish, use final_answer("your response").
        """,
        max_steps=12
    )
    
    return manager, state_manager, rag_pipeline
