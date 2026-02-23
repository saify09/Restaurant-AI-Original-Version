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
        YOU ARE THE CEO. You MUST use your specialists to answer queries.
        
        - menu_agent: For ANY food/menu lookup.
        - transaction_agent: For orders, status, and refunds.
        - compliance_agent: For policy checks.
        
        STRICT RULES:
        1. YOU MUST CALL AN AGENT to get data. DO NOT guess or ask for context.
        2. FORMAT: You MUST follow the 'Thought' + 'Code' pattern exactly.
        3. CODE BLOCK: Use '<code>' tags for Python code, NOT markdown backticks.
        
        Example Output Format:
        Thought: I will ask the menu agent for the current menu items.
        <code>
        menu_agent(task="Show me the full menu items and prices")
        </code>
        """,
        max_steps=12,
        additional_authorized_imports=['pandas', 'json', 'time', 'datetime']
    )
    
    return manager, state_manager, rag_pipeline
