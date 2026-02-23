# 🍊 Autonomous Restaurant AI Platform

**100% free. No paid APIs. Runs on Hugging Face Spaces free CPU tier.**

---

## 📁 File Structure

```
restaurant_ai/
├── app.py                  ← Gradio UI entry point
├── agents.py               ← Rule-based ManagerAgent (no LLM API needed)
├── transaction_service.py  ← Order + refund logic
├── rag_service.py          ← Menu & policy parsing
├── auth_service.py         ← RBAC
├── audit_service.py        ← Immutable audit log
├── dashboards.py           ← View helpers
├── state.py                ← In-memory store (Redis mock)
├── requirements.txt
└── docs/
    ├── menu.md
    └── policies.md
```

---

## 🚀 Deploy on Hugging Face Spaces (Free)

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Choose **Gradio** SDK · **CPU Free** hardware
4. Upload **all files** maintaining the exact structure above
5. HF will automatically install `requirements.txt`
6. Click **Deploy** — done!

---

## 💬 Customer Commands

| Command | Example |
|---|---|
| View menu | `menu` or `help` |
| Place order | `order Burger` / `I'd like a Pizza` |
| Cancel order | `cancel <order-id>` |
| Check balance | `balance` |

---

## 👤 Default Accounts

| Username | Balance | Role |
|---|---|---|
| `customer` | $100.00 | Customer |
| `admin` | $0.00 | Admin |
| `superadmin` | $0.00 | SuperAdmin |

Any new username typed in the portal gets a $50.00 starting balance automatically.

---

## 🏗️ Architecture

```
User Input
    │
    ▼
ManagerAgent          ← Rule-based NLP (regex, no LLM cost)
    │
    ├─► RAGService     ← Reads docs/menu.md + docs/policies.md locally
    ├─► AuthService    ← RBAC permission checks
    ├─► TransactionService ← Order/refund with inventory + balance updates
    └─► AuditService   ← Append-only event log
```

All data lives in memory (RedisMock). On HF Spaces, state resets on restart —
this is expected for a free-tier demo. To persist, swap RedisMock for
SQLite (still free) or a free-tier Upstash Redis instance.

---

## 🔒 Business Rules

- Refunds allowed within **10 minutes** of order
- No refund once status is `PREPARING` or `COMPLETED`
- All decisions are logged with risk level to the audit trail
