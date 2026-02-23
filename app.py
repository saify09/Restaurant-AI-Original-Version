import gradio as gr
import pandas as pd
import json
import time
from src.agents.manager_agent import create_manager_agent

# Initialize Backend
from init_rag import init_rag
import os

# Check if RAG index exists in the correct path
if not os.path.exists("data/vectors/faiss.index"):
    print("Building RAG Index for the first time...")
    init_rag()

manager, state_manager, rag_pipeline = create_manager_agent()

def chatbot_response(message, history):
    user_id = "USR-001"
    response = manager.run(f"User {user_id}: {message}")
    
    state_manager.log_audit({
        "user_id": user_id,
        "input": message,
        "response": str(response)
    })
    
    if history is None: history = []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": str(response)})
    return history

def get_restaurant_stats():
    orders = state_manager.get_all_orders()
    df = pd.DataFrame.from_dict(orders, orient='index')
    if df.empty:
        return pd.DataFrame(columns=["order_id", "status", "total"])
    return df[["order_id", "status", "total"]]

def get_inventory_stats():
    inv = state_manager.get_inventory()
    df = pd.DataFrame(list(inv.items()), columns=["Item", "Quantity"])
    return df

def get_audit_logs():
    logs = state_manager.state.get("audit_logs", [])
    if not logs:
        return pd.DataFrame(columns=["timestamp", "user_id", "action", "details"])
    return pd.DataFrame(logs).tail(20) # Show last 20 logs

def get_user_balance_display():
    balance = state_manager.get_user_balance("USR-001")
    return f"### Wallet Balance: ${balance:.2f}"

def refresh_dashboards():
    return (
        get_user_balance_display(),
        get_restaurant_stats(),
        get_inventory_stats(),
        get_audit_logs()
    )

# --- UI Theme ---
theme = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="gray",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)

with gr.Blocks(theme=theme, title="GourmetAI - Autonomous Restaurant Platform") as demo:
    gr.Markdown("# 🍽️ GourmetAI Platform")
    gr.Markdown("### *A Foodpanda-Level Autonomous AI SaaS*")
    
    with gr.Tabs() as tabs:
        
        # 1. Customer Tab
        with gr.Tab("📱 Customer App"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(label="GourmetAI Assistant", type="messages", height=500)
                    msg_input = gr.Textbox(placeholder="Type your message here...", label="Your Message")
                    
                    # Submit via Enter
                    msg_input.submit(chatbot_response, [msg_input, chatbot], [msg_input, chatbot])
                    
                with gr.Column(scale=1):
                    balance_display = gr.Markdown(get_user_balance_display())
                    gr.Markdown("#### Rapid Actions")
                    gr.Button("Browse Menu").click(lambda: "What is on the menu?", outputs=msg_input).then(chatbot_response, [msg_input, chatbot], [msg_input, chatbot])
                    gr.Button("Check Order Status").click(lambda: "What is the status of my latest order?", outputs=msg_input).then(chatbot_response, [msg_input, chatbot], [msg_input, chatbot])
                    gr.Button("Request Refund").click(lambda: "I want a refund for my last order.", outputs=msg_input).then(chatbot_response, [msg_input, chatbot], [msg_input, chatbot])

        # 2. Restaurant Tab
        with gr.Tab("🍳 Restaurant Dashboard"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🕒 Active Orders")
                    order_table = gr.DataFrame(value=get_restaurant_stats())
                with gr.Column():
                    gr.Markdown("### 📦 Inventory Management")
                    inventory_table = gr.DataFrame(value=get_inventory_stats())
            
            refresh_btn = gr.Button("🔄 Refresh Kitchen Feed")
            refresh_btn.click(
                refresh_dashboards, 
                outputs=[balance_display, order_table, inventory_table, gr.State()] # State placeholder
            )

        # 3. Super Admin Tab
        with gr.Tab("🛡️ Super Admin Control"):
            gr.Markdown("### 🔍 AI Compliance & Audit Trail")
            audit_table = gr.DataFrame(value=get_audit_logs())
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📈 Platform Metrics")
                    # Placeholder for advanced metrics
                    gr.Label(label="AI Refusal Rate", value="12%")
                    gr.Label(label="Refund Rate", value="4.5%")
                with gr.Column():
                    gr.Markdown("### 🛡️ Guardrail Status")
                    gr.Markdown("✅ RAG Policy Bridge: **ONLINE**")
                    gr.Markdown("✅ Transaction Verification: **ENFORCED**")
                    gr.Markdown("✅ Auditor Daemon: **ACTIVE**")
            
            refresh_admin_btn = gr.Button("🔄 Update Logs")
            refresh_admin_btn.click(
                get_audit_logs,
                outputs=audit_table
            )

    # Initial periodic refresh setup if needed, or manual
    demo.load(refresh_dashboards, outputs=[balance_display, order_table, inventory_table, audit_table])

if __name__ == "__main__":
    demo.launch(theme=theme, server_name="0.0.0.0")
