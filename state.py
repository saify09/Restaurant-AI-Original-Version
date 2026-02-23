"""
state.py - In-memory state store (simulates Redis for HF Spaces free tier)
"""


class RedisMock:
    def __init__(self):
        self.store = {
            "users": {
                "customer": {"balance": 100.0, "role": "Customer"},
                "admin":    {"balance": 0.0,   "role": "Admin"},
                "superadmin": {"balance": 0.0, "role": "SuperAdmin"},
            },
            "orders": {},
            "inventory": {
                "Burger": 10,
                "Pizza":  5,
                "Pasta":  7,
            },
        }

    def get(self, namespace, key=None):
        if key is not None:
            return self.store.get(namespace, {}).get(key)
        return self.store.get(namespace, {})

    def set(self, namespace, key, value):
        self.store.setdefault(namespace, {})[key] = value

    def delete(self, namespace, key):
        self.store.get(namespace, {}).pop(key, None)


redis_db = RedisMock()
