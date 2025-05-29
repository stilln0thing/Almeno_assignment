# 💳 Credit Approval System

A backend-only, Dockerized Django application for managing customer credit approvals based on historical loan data and income. Includes asynchronous data ingestion with Celery and Redis.

---

## 🚀 Features

- Register new customers and auto-calculate approved credit limits.
- Background ingestion of historical customer and loan data via Celery.
- Real-time credit score calculation based on multiple criteria.
- Intelligent loan approval/rejection with EMI and interest rate corrections.
- View individual loans and customer loan history.

---

## 🛠 Tech Stack

- **Backend**: Django 4+, Django REST Framework
- **Database**: PostgreSQL
- **Asynchronous Tasks**: Celery with Redis broker
- **Containerization**: Docker & Docker Compose
- **Data Processing**: Pandas (Excel ingestion)

---

## 🧱 Project Structure

├── core/ # Models & serializers for Customer, Loan
├── credit_approval/ # Business logic & API views
├── docker/ # Docker-specific configs (optional)
├── manage.py
├── docker-compose.yml
└── README.md