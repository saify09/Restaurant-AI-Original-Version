---
title: Restaurant AI Gradio Version
emoji: 🍊
colorFrom: yellow
colorTo: green
sdk: gradio
sdk_version: "5.0.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🍊 Autonomous Restaurant AI Platform

**100% free. No paid APIs. Runs on Hugging Face Spaces free CPU tier.**

A rule-based AI-powered restaurant management system built with Python and Gradio. This platform allows customers to interact via a chat interface to view menus, place orders, check balances, and manage refunds. Admins can monitor orders, inventory, and audit logs through dedicated dashboards. All operations are handled by lightweight, cost-free services without relying on external LLM APIs.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Business Rules](#business-rules)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Customer Portal**: Interactive chat interface for menu browsing, ordering, balance checking, and order management.
- **Admin Dashboard**: Real-time views of all orders and inventory levels.
- **Audit Log**: Immutable event logging for all transactions and decisions with risk assessment.
- **Authentication & Authorization**: Role-Based Access Control (RBAC) with default accounts for customers, admins, and superadmins.
- **Transaction Management**: Secure order placement, refunds, and cancellations with inventory tracking.
- **RAG Service**: Parses local menu and policy documents for dynamic responses.
- **In-Memory State**: Uses a Redis mock for data storage (resets on restart for free-tier demos).
- **Free Hosting**: Optimized for Hugging Face Spaces free CPU tier.

## 🏗️ Architecture

The platform follows a modular service-oriented architecture:

```
User Input (Gradio UI)
    │
    ▼
ManagerAgent          ← Rule-based NLP (regex-based, no LLM cost)
    │
    ├─► RAGService     ← Reads docs/menu.md + docs/policies.md locally
    ├─► AuthService    ← RBAC permission checks
    ├─► TransactionService ← Order/refund with inventory + balance updates
    └─► AuditService   ← Append-only event log
```

- **ManagerAgent**: Processes user commands using regex patterns for intent recognition.
- **RAGService**: Retrieves and parses menu and policy information from local Markdown files.
- **AuthService**: Manages user roles and permissions.
- **TransactionService**: Handles order lifecycle, inventory, and financial transactions.
- **AuditService**: Logs all events with timestamps and risk levels.
- **State**: In-memory data store mimicking Redis for users, orders, and inventory.

All data is stored in memory and resets on application restart, suitable for demo purposes. For persistence, consider integrating SQLite or a free Redis instance.

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/your-repo/restaurant-ai-platform.git
   cd restaurant-ai-platform
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

   The Gradio interface will launch in your browser at `http://localhost:7860`.

## 🚀 Usage

### Customer Portal

- **Login**: Enter a username (e.g., `customer`, `admin`, `superadmin`). New users get a $50.00 starting balance.
- **Commands**:
  - `menu` or `help`: View the menu.
  - `order <item>`: Place an order (e.g., `order Burger`).
  - `cancel <order-id>`: Cancel an order.
  - `balance`: Check account balance.
- **Interface**: Use the chat interface to interact naturally (e.g., "I'd like a Pizza").

### Admin Dashboard

- Access the "Admin Dashboard" tab to view all orders and inventory.
- Refresh data using the provided buttons.

### Audit Log

- Superadmins can access the "Audit Log" tab for a full event trail.

### Default Accounts

| Username    | Balance | Role       |
|-------------|---------|------------|
| `customer`  | $100.00 | Customer   |
| `admin`     | $0.00   | Admin      |
| `superadmin`| $0.00   | SuperAdmin |

## 🌐 Deployment

For detailed deployment instructions on Hugging Face Spaces, refer to [README_DEPLOYMENT.md](README_DEPLOYMENT.md).

### Quick Deploy Steps

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Select **Gradio** SDK and **CPU Free** hardware.
3. Upload all project files maintaining the directory structure.
4. Deploy – Hugging Face will handle dependency installation.

## 📜 Business Rules

- **Refunds**: Allowed within 10 minutes of order placement. Not permitted once the order status is `PREPARING` or `COMPLETED`.
- **Cancellations**: Permitted before preparation begins.
- **Inventory**: Orders deduct from available stock; insufficient inventory blocks orders.
- **Balances**: Users must have sufficient funds; new users start with $50.00.
- **Audit**: All actions are logged with risk levels (e.g., high-risk refunds).

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -m 'Add your feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a Pull Request.

Ensure code follows PEP 8 standards and includes tests where applicable.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using Python, Gradio, and a passion for efficient AI.</content>
<parameter name="filePath">D:\Restaurant\README.md