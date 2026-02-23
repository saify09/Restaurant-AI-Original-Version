"""
agents.py - Rule-based ManagerAgent (zero cost, no external API)

Understands natural-language commands:
  • "order Burger"  /  "I'd like a Pizza"  /  "get me Pasta"
  • "cancel <order-id>"
  • "menu"  /  "help"
  • "balance"
"""

import re
from transaction_service import transaction_service
from rag_service import rag_service
from state import redis_db

MENU_ITEMS = []  # populated lazily


def _get_menu_items():
    global MENU_ITEMS
    if not MENU_ITEMS:
        MENU_ITEMS = rag_service.get_menu()["Item"].str.strip().tolist()
    return MENU_ITEMS


ORDER_TRIGGERS  = re.compile(r"\b(order|get|buy|want|place|give me|i'd like|i want|can i have)\b", re.I)
CANCEL_TRIGGERS = re.compile(r"\b(cancel|refund|undo)\b", re.I)
UUID_PATTERN    = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


class ManagerAgent:
    def route(self, user_input: str, user: str = "customer") -> str:
        text = user_input.strip()

        # ── help / menu ────────────────────────────────────────────────
        if re.search(r"\b(help|menu|what (can|do) you|options)\b", text, re.I):
            return self._help_text()

        # ── balance inquiry ────────────────────────────────────────────
        if re.search(r"\b(balance|credit|funds|money)\b", text, re.I):
            user_data = redis_db.get("users", user)
            if user_data:
                return f"💰 Your current balance is **${user_data['balance']:.2f}**"
            return "❌ User not found."

        # ── cancel / refund ────────────────────────────────────────────
        if CANCEL_TRIGGERS.search(text):
            uid_match = UUID_PATTERN.search(text)
            if uid_match:
                return transaction_service.cancel_order(user, uid_match.group(0))
            return (
                "⚠️ Please provide the Order ID to cancel.\n"
                "Example: `cancel 3f2a1b00-...`"
            )

        # ── place order ────────────────────────────────────────────────
        if ORDER_TRIGGERS.search(text):
            items = _get_menu_items()
            for item in items:
                if item.lower() in text.lower():
                    return transaction_service.place_order(user, item)
            # Fallback: last word might be the item
            last_word = text.split()[-1].strip(".,!?")
            return transaction_service.place_order(user, last_word)

        # ── direct item name ───────────────────────────────────────────
        items = _get_menu_items()
        for item in items:
            if item.lower() in text.lower():
                return transaction_service.place_order(user, item)

        return (
            "🤔 I didn't understand that. Try:\n"
            "• `order Burger`\n"
            "• `cancel <order-id>`\n"
            "• `menu` to see what's available\n"
            "• `balance` to check your funds"
        )

    def _help_text(self) -> str:
        items = _get_menu_items()
        menu = rag_service.get_menu()
        lines = ["**🍽️ Menu**\n"]
        for _, row in menu.iterrows():
            lines.append(f"• **{row['Item'].strip()}** — ${float(row['Price']):.2f}")
        lines += [
            "\n**💬 Commands**",
            "• `order <item>` — place an order",
            "• `cancel <order-id>` — request a refund",
            "• `balance` — check your balance",
            "• `menu` / `help` — show this message",
        ]
        return "\n".join(lines)


manager_agent = ManagerAgent()
