"""
app.py - Autonomous Restaurant AI Platform
100% free · No paid APIs · Hugging Face Spaces ready
"""

import gradio as gr

from agents import manager_agent
from dashboards import dashboards
from rag_service import rag_service
from state import redis_db

# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:       #0a0c10;
    --surface:  #111318;
    --border:   #1e2230;
    --accent:   #f97316;
    --accent2:  #fb923c;
    --text:     #e8eaf0;
    --muted:    #6b7280;
    --green:    #22c55e;
    --red:      #ef4444;
}

* { box-sizing: border-box; }

body, .gradio-container {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

/* Tab bar */
.tab-nav button {
    background: transparent !important;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
}
.tab-nav button.selected {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: transparent !important;
}

/* Buttons */
button.lg, button.primary {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    transition: opacity 0.15s !important;
}
button.lg:hover, button.primary:hover { opacity: 0.85 !important; }

/* Chat bubbles */
.message.user   { background: #1a2035 !important; border-left: 3px solid var(--accent) !important; }
.message.bot    { background: var(--surface) !important; border-left: 3px solid var(--green) !important; }
.message        { font-family: 'DM Mono', monospace !important; font-size: 0.88rem !important; border-radius: 8px !important; }

/* Textbox */
textarea, input[type=text] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 6px !important;
}

/* JSON output */
.json-holder { background: var(--surface) !important; border-radius: 8px !important; }

/* Header */
#header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
    margin-bottom: 8px;
}
#header h1 { font-size: 1.8rem; font-weight: 800; margin: 0; }
#header h1 span { color: var(--accent); }
#header p  { color: var(--muted); margin: 4px 0 0; font-size: 0.85rem; }

/* Menu cards */
.menu-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 6px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.menu-card .item-name { font-weight: 700; font-size: 1rem; }
.menu-card .item-price { color: var(--accent); font-family: 'DM Mono', monospace; font-weight: 600; }
.menu-card .item-ing  { color: var(--muted); font-size: 0.8rem; }
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def build_menu_html() -> str:
    df = rag_service.get_menu()
    rows = ""
    for _, r in df.iterrows():
        rows += (
            f'<div class="menu-card">'
            f'  <div>'
            f'    <div class="item-name">{r["Item"].strip()}</div>'
            f'    <div class="item-ing">{r["Ingredients"].strip()}</div>'
            f'  </div>'
            f'  <div class="item-price">${float(r["Price"]):.2f}</div>'
            f'</div>'
        )
    return rows


def customer_chat(message: str, history: list, username: str) -> str:
    user = username.strip().lower() or "customer"
    if user not in redis_db.get("users", None) if False else redis_db.store["users"]:
        # Auto-create unknown users with $50 balance
        redis_db.store["users"][user] = {"balance": 50.0, "role": "Customer"}
    return manager_agent.route(message, user=user)


def refresh_customer(username: str) -> dict:
    user = username.strip().lower() or "customer"
    return dashboards.customer_view(user)


# ── App ───────────────────────────────────────────────────────────────────────

with gr.Blocks(css=CSS, title="🍊 Restaurant AI") as app:

    # Header
    gr.HTML("""
    <div id="header">
        <h1>🍊 Restaurant <span>AI</span></h1>
        <p>Autonomous ordering platform · 100% free · no external APIs</p>
    </div>
    """)

    with gr.Tabs():

        # ── CUSTOMER PORTAL ──────────────────────────────────────────────
        with gr.Tab("🛒 Customer Portal"):
            with gr.Row():
                with gr.Column(scale=2):
                    username_box = gr.Textbox(
                        value="customer",
                        label="Username",
                        placeholder="customer / admin / superadmin",
                        max_lines=1,
                    )
                    chatbot = gr.ChatInterface(
                        fn=customer_chat,
                        additional_inputs=[username_box],
                        examples=[
                            ["menu"],
                            ["order Burger"],
                            ["order Pizza"],
                            ["balance"],
                        ],
                        chatbot=gr.Chatbot(height=380, render_markdown=True),
                        textbox=gr.Textbox(placeholder="Type a command...", max_lines=1),
                    )

                with gr.Column(scale=1):
                    gr.HTML("<h3 style='color:#f97316;margin:0 0 8px'>🍽️ Today's Menu</h3>")
                    gr.HTML(build_menu_html())
                    gr.HTML("<br>")
                    gr.HTML("<h3 style='color:#f97316;margin:0 0 8px'>📊 My Account</h3>")
                    customer_json = gr.JSON(label="")
                    refresh_btn = gr.Button("🔄 Refresh Account", size="sm")
                    refresh_btn.click(
                        fn=refresh_customer,
                        inputs=[username_box],
                        outputs=[customer_json],
                    )

        # ── ADMIN DASHBOARD ──────────────────────────────────────────────
        with gr.Tab("🔧 Admin Dashboard"):
            gr.HTML("<h3 style='color:#f97316'>All Orders</h3>")
            admin_json = gr.JSON(label="Orders")
            with gr.Row():
                gr.Button("🔄 Refresh Orders").click(
                    fn=dashboards.admin_view, outputs=[admin_json]
                )

            gr.HTML("<h3 style='color:#f97316;margin-top:16px'>Inventory</h3>")
            inv_json = gr.JSON(label="Inventory")
            gr.Button("🔄 Refresh Inventory").click(
                fn=dashboards.inventory_view, outputs=[inv_json]
            )

        # ── SUPERADMIN AUDIT ─────────────────────────────────────────────
        with gr.Tab("🛡️ Audit Log"):
            gr.HTML("<h3 style='color:#f97316'>Full Audit Trail</h3>")
            audit_json = gr.JSON(label="Audit Events")
            gr.Button("🔄 View Logs").click(
                fn=dashboards.audit_view, outputs=[audit_json]
            )

app.launch()
