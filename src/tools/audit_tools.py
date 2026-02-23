from smolagents import Tool
from src.utils.state_manager import StateManager
from typing import Dict, Any

class AuditTool(Tool):
    name = "audit_log"
    description = "Logs an AI decision to the audit trail. Use this for every final decision, especially refunds, cancellations, and status changes."
    inputs = {
        "user_id": {"type": "string", "description": "The ID of the user"},
        "action": {"type": "string", "description": "The action taken (e.g. 'REFUND_APPROVED', 'ORDER_CREATED')"},
        "reasoning": {"type": "string", "description": "Detailed reasoning summary for the action"},
        "risk_level": {"type": "string", "description": "Risk assessment: Low, Medium, or High"},
        "compliance_citation": {"type": "string", "description": "If applicable, the policy or T&C section used for the decision", "nullable": True}
    }
    output_type = "string"

    def __init__(self, state_manager: StateManager, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = state_manager

    def forward(self, user_id: str, action: str, reasoning: str, risk_level: str, compliance_citation: str = "N/A") -> str:
        log_entry = {
            "user_id": user_id,
            "action": action,
            "reasoning": reasoning,
            "risk_level": risk_level,
            "compliance_citation": compliance_citation
        }
        self.state_manager.log_audit(log_entry)
        return "Decision logged to audit trail."
