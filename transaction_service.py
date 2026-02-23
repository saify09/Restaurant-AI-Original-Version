"""
transaction_service.py - Core order and refund logic
"""

import datetime
import uuid

from audit_service import audit_service
from rag_service import rag_service
from state import redis_db


class TransactionService:
    def place_order(self, user: str, item: str) -> str:
        price_info = rag_service.get_price(item)
        if not price_info.get("item_exists"):
            return f"❌ Item '{item}' not found on the menu."

        canonical = price_info["canonical_name"]
        price = price_info["price"]

        inventory = redis_db.get("inventory", canonical)
        if inventory is None or inventory <= 0:
            return f"❌ Sorry, '{canonical}' is currently out of stock."

        user_data = redis_db.get("users", user)
        if user_data is None:
            return "❌ User account not found."
        if user_data["balance"] < price:
            return (
                f"❌ Insufficient balance. You have ${user_data['balance']:.2f} "
                f"but '{canonical}' costs ${price:.2f}."
            )

        order_id = str(uuid.uuid4())
        redis_db.store["orders"][order_id] = {
            "item":   canonical,
            "price":  price,
            "status": "PLACED",
            "time":   datetime.datetime.utcnow(),
            "user":   user,
        }
        redis_db.store["inventory"][canonical] -= 1
        redis_db.store["users"][user]["balance"] -= price

        audit_service.log(user, "Customer", "TransactionAgent", "place_order", "APPROVED")
        new_balance = redis_db.store["users"][user]["balance"]
        return (
            f"✅ Order placed successfully!\n"
            f"📦 Item: {canonical} — ${price:.2f}\n"
            f"🆔 Order ID: `{order_id}`\n"
            f"💰 Remaining balance: ${new_balance:.2f}"
        )

    def cancel_order(self, user: str, order_id: str) -> str:
        order_id = order_id.strip()
        order = redis_db.get("orders", order_id)
        if not order:
            return f"❌ No order found with ID: `{order_id}`"

        if order["user"] != user:
            audit_service.log(user, "Customer", "TransactionAgent", "cancel", "DENIED", "HIGH", "Unauthorized")
            return "❌ You are not authorized to cancel this order."

        if order["status"] in ("CANCELLED", "REFUNDED"):
            return f"⚠️ This order has already been {order['status'].lower()}."

        allowed = rag_service.check_refund_policy(order["time"], order["status"])
        if not allowed:
            audit_service.log(user, "Customer", "TransactionAgent", "cancel", "DENIED", "HIGH", "Policy violation")
            return (
                "❌ Refund denied by policy.\n"
                "Orders can only be refunded within 10 minutes and before preparation begins."
            )

        order["status"] = "REFUNDED"
        redis_db.store["users"][user]["balance"] += order["price"]
        redis_db.store["inventory"][order["item"]] += 1

        audit_service.log(user, "Customer", "TransactionAgent", "cancel", "APPROVED")
        new_balance = redis_db.store["users"][user]["balance"]
        return (
            f"✅ Order refunded successfully!\n"
            f"💰 ${order['price']:.2f} returned. New balance: ${new_balance:.2f}"
        )


transaction_service = TransactionService()
