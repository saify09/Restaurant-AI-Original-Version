"""
audit_service.py - Immutable audit log for all agent decisions
"""

import datetime


class AuditService:
    def __init__(self):
        self.logs = []

    def log(self, user, role, agent, action, decision, risk="LOW", reason=""):
        self.logs.append({
            "timestamp": str(datetime.datetime.utcnow()),
            "user":      user,
            "role":      role,
            "agent":     agent,
            "action":    action,
            "decision":  decision,
            "risk":      risk,
            "reason":    reason,
        })

    def get_logs(self):
        return list(self.logs)


audit_service = AuditService()
