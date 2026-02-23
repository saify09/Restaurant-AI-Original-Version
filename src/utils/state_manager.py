import json
import os
import time
from typing import Dict, Any, List

class StateManager:
    def __init__(self, storage_path: str = "data/state.json"):
        self.storage_path = storage_path
        self._ensure_storage()
        self.state = self._load_state()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            initial_state = {
                "orders": {},
                "inventory": {
                    "Burger": 50,
                    "Pizza": 30,
                    "Pasta": 25,
                    "Coke": 100,
                    "Salad": 40
                },
                "users": {
                    "USR-001": {"balance": 100.0, "name": "Demo User"}
                },
                "refunds": [],
                "audit_logs": []
            }
            with open(self.storage_path, 'w') as f:
                json.dump(initial_state, f, indent=4)

    def _load_state(self) -> Dict[str, Any]:
        with open(self.storage_path, 'r') as f:
            return json.load(f)

    def _save_state(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def get_user_balance(self, user_id: str) -> float:
        return self.state["users"].get(user_id, {}).get("balance", 0.0)

    def update_user_balance(self, user_id: str, amount: float):
        if user_id in self.state["users"]:
            self.state["users"][user_id]["balance"] += amount
            self._save_state()

    def create_order(self, user_id: str, items: List[Dict[str, Any]], total: float) -> str:
        order_id = f"ORD-{int(time.time())}"
        self.state["orders"][order_id] = {
            "order_id": order_id,
            "user_id": user_id,
            "items": items,
            "total": total,
            "status": "PENDING",
            "timestamp": time.time()
        }
        self._save_state()
        return order_id

    def update_order_status(self, order_id: str, status: str):
        if order_id in self.state["orders"]:
            self.state["orders"][order_id]["status"] = status
            self._save_state()

    def check_inventory(self, item: str, quantity: int) -> bool:
        return self.state["inventory"].get(item, 0) >= quantity

    def reduce_inventory(self, item: str, quantity: int):
        if self.check_inventory(item, quantity):
            self.state["inventory"][item] -= quantity
            self._save_state()

    def log_audit(self, entry: Dict[str, Any]):
        self.state["audit_logs"].append({
            "timestamp": time.time(),
            **entry
        })
        self._save_state()

    def get_all_orders(self) -> Dict[str, Any]:
        return self.state["orders"]

    def get_inventory(self) -> Dict[str, int]:
        return self.state["inventory"]
