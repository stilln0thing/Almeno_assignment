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

| Path                      | Description                                           |
|---------------------------|-------------------------------------------------------|
| `core/`                   | Models and serializers for `Customer` and `Loan`     |
| `credit_approval/`        | Business logic and API views for loan processing     |
| `data/`                   | Contains `customer_data.xlsx` and `loan_data.xlsx`   |
| `docker/`                 | Docker-specific configs (e.g., `Dockerfile`, etc.)   |
| `manage.py`               | Django project entry point                           |
| `docker-compose.yml`      | Docker Compose file to spin up all services          |
| `README.md`               | Project documentation                                |

## ⚙️ Setup Instructions

## Clone the Repository

```bash
git clone https://github.com/<your-username>/credit-approval-system.git
cd credit-approval-system

2. Add .env File
Create a .env file in the root directory:

POSTGRES_DB=credit_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

3. Start the App with Docker

```bash
docker-compose up --build
```


## API Endpoints
1. POST /register
Register a new customer.

2. POST /check-eligibility
Calculate credit score and assess loan eligibility.

3. POST /create-loan
Create a loan if eligible. Automatically stores loan data.

4. GET /view-loan/<loan_id>
View loan and customer info for a specific loan.

5. GET /view-loans/<customer_id>
View all current loans and repayments_left for a customer.
