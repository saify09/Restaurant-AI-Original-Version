from smolagents import Tool
from src.utils.state_manager import StateManager
from src.utils.rag_pipeline import RAGPipeline
from typing import Dict, Any, List
import time

class CreateOrderTool(Tool):
    name = "create_order"
    description = "Creates a new order for a user. Items should be a list of dictionaries with 'item' and 'quantity'."
    inputs = {
        "user_id": {"type": "string", "description": "The ID of the user"},
        "items": {"type": "any", "description": "List of items e.g. [{'item': 'Burger', 'quantity': 1}]"},
        "total": {"type": "number", "description": "The total price of the order"}
    }
    output_type = "string"

    def __init__(self, state_manager: StateManager, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = state_manager

    def forward(self, user_id: str, items: List[Dict[str, Any]], total: float) -> str:
        order_id = self.state_manager.create_order(user_id, items, total)
        return f"Order created successfully. Order ID: {order_id}"

class GetOrderStatusTool(Tool):
    name = "get_order_status"
    description = "Retrieves the status of an existing order."
    inputs = {
        "order_id": {"type": "string", "description": "The ID of the order"}
    }
    output_type = "string"

    def __init__(self, state_manager: StateManager, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = state_manager

    def forward(self, order_id: str) -> str:
        orders = self.state_manager.get_all_orders()
        order = orders.get(order_id)
        if order:
            return f"Order {order_id} status: {order['status']}"
        return "Order not found."

class RefundRequestTool(Tool):
    name = "request_refund"
    description = "Requests a refund for an order. MUST call verify_compliance first."
    inputs = {
        "order_id": {"type": "string", "description": "The ID of the order"},
        "reason": {"type": "string", "description": "Reason for refund"}
    }
    output_type = "string"

    def __init__(self, state_manager: StateManager, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = state_manager

    def forward(self, order_id: str, reason: str) -> str:
        orders = self.state_manager.get_all_orders()
        order = orders.get(order_id)
        if not order:
            return "Order not found."
            
        self.state_manager.update_order_status(order_id, "REFUND_PENDING")
        self.state_manager.state["refunds"].append({
            "order_id": order_id,
            "reason": reason,
            "timestamp": time.time()
        })
        self.state_manager._save_state()
        return "Refund request submitted and pending approval."
