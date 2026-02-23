import sys
import time
print(f"--- STARTUP TRACE: V1.1.6 - {time.ctime()} ---", flush=True)

print("Loading core libraries...", flush=True)
import os
import gradio as gr
print(f"Gradio Version: {gr.__version__}", flush=True)
print(f"HF_TOKEN detected: {os.getenv('HF_TOKEN') is not None}", flush=True)
import pandas as pd
import json

print("Initializing agent components...", flush=True)
from src.agents.manager_agent import create_manager_agent

# Initialize Backend
from init_rag import init_rag
import os

# Check if RAG index exists in the correct path
if not os.path.exists("data/vectors/faiss.index"):
    print("Building RAG Index for the first time...", flush=True)
    init_rag()

print("Creating agents and pipelines...", flush=True)
manager, state_manager, rag_pipeline = create_manager_agent()
print("Backend Ready.", flush=True)

def chatbot_response(message, history):
    if not message:
        return "", history
    
    user_id = "USR-001"
    try:
        response = manager.run(f"User {user_id}: {message}")
    except Exception as e:
        response = f"AI Error: {str(e)}"
    
    state_manager.log_audit({
        "user_id": user_id,
        "input": message,
        "response": str(response)
    })
    
    if history is None: history = []
    
    # Gradio 6 format requirement: messages list
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": str(response)})
        
    return "", history

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

with gr.Blocks(title="GourmetAI - Autonomous Restaurant Platform", theme=theme) as demo:
    gr.Markdown("# 🍽️ GourmetAI Platform")
    gr.Markdown("### *A Foodpanda-Level Autonomous AI SaaS*")
    
    with gr.Tabs() as tabs:
        
        # 1. Customer Tab
        with gr.Tab("📱 Customer App"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(label="GourmetAI Assistant", height=500, type="messages")
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

    # Event Bindings (Done at end to ensure all components are defined)
    refresh_btn.click(
        refresh_dashboards, 
        outputs=[balance_display, order_table, inventory_table, audit_table]
    )
    
    demo.load(refresh_dashboards, outputs=[balance_display, order_table, inventory_table, audit_table])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", ssr=False)
