"""
dashboards.py - View helpers for Customer, Admin, and SuperAdmin tabs
"""

from audit_service import audit_service
from state import redis_db


class Dashboards:
    def customer_view(self, user: str) -> dict:
        orders = {
            oid: o
            for oid, o in redis_db.get("orders").items()
            if o["user"] == user
        }
        # Convert datetime objects to strings for JSON serialisation
        serialisable = {}
        for oid, o in orders.items():
            serialisable[oid] = {**o, "time": str(o["time"])}

        balance = redis_db.get("users", user)["balance"]
        return {"balance": f"${balance:.2f}", "orders": serialisable}

    def admin_view(self) -> dict:
        result = {}
        for oid, o in redis_db.get("orders").items():
            result[oid] = {**o, "time": str(o["time"])}
        return result

    def inventory_view(self) -> dict:
        return dict(redis_db.get("inventory"))

    def audit_view(self) -> list:
        return audit_service.get_logs()


dashboards = Dashboards()
