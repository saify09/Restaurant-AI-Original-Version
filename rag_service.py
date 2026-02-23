"""
rag_service.py - Menu lookup and policy enforcement (no paid API required)
Parses docs/menu.md and docs/policies.md locally.
"""

import datetime
import os
import pandas as pd


class RAGService:
    def __init__(self):
        menu_path = os.path.join(os.path.dirname(__file__), "docs", "menu.md")
        # Parse markdown pipe table; skip the separator row (row index 1)
        rows = []
        with open(menu_path, "r") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith("|--") or line.startswith("| --"):
                    continue
                parts = [p.strip() for p in line.strip("|").split("|")]
                rows.append(parts)

        if len(rows) >= 2:
            headers = rows[0]
            data = rows[1:]
            self.menu = pd.DataFrame(data, columns=headers)
        else:
            self.menu = pd.DataFrame(columns=["Item", "Price", "Ingredients", "Available"])

    def get_menu(self) -> pd.DataFrame:
        return self.menu

    def get_price(self, item: str) -> dict:
        row = self.menu[self.menu["Item"].str.strip().str.lower() == item.strip().lower()]
        if row.empty:
            return {"item_exists": False}
        try:
            price = float(row["Price"].values[0])
        except (ValueError, IndexError):
            return {"item_exists": False}
        return {"item_exists": True, "price": price, "canonical_name": row["Item"].values[0].strip()}

    def check_refund_policy(self, order_time: datetime.datetime, status: str) -> bool:
        if status in ("PREPARING", "COMPLETED"):
            return False
        elapsed = (datetime.datetime.utcnow() - order_time).total_seconds()
        return elapsed <= 600  # 10-minute window


rag_service = RAGService()
