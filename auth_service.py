"""
auth_service.py - Role-based access control
"""

from state import redis_db

PERMISSIONS = {
    "Customer":   ["order", "cancel", "view"],
    "Admin":      ["view_all", "update"],
    "SuperAdmin": ["audit", "override"],
}


class AuthService:
    def get_role(self, username: str) -> str | None:
        user = redis_db.get("users", username)
        return user.get("role") if user else None

    def check_permission(self, role: str, action: str) -> bool:
        return action in PERMISSIONS.get(role, [])


auth_service = AuthService()
