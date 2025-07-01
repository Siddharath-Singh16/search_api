# 🚀 HR Employee Search Microservice

A scalable and modular FastAPI-based microservice for searching employees, featuring dynamic column visibility, thread-safe rate limiting, and containerized deployment.

---

## 📁 Features

✅ **FastAPI Microservice**
✅ **Search API** with filtering, pagination
✅ **Dynamic Columns** per organization
✅ **Thread-safe Rate Limiter Middleware** (configurable requests per organization)
✅ **Alembic Migrations**
✅ **SQLite support**
✅ **Dockerized deployment**
✅ **Unit Tests with Pytest**

---

## 📦 Requirements

* Python 3.11+
* Docker (optional)
* pip (for local setup)

---

## 🏗️ Project Structure

```
hr_system/
├── src/
│   ├── api/               # FastAPI endpoints
│   ├── middleware/        # Rate limiter middleware
│   ├── db/                # Session, base, seed logic
│   ├── models/            # SQLAlchemy models
│   ├── org_config/        # Per-org column visibility
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   └── main.py            # App entry point
├── alembic/               # Alembic migrations
├── tests/                 # Pytest tests
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## 🧑‍💻 Getting Started

### 🐳 Option 1: Docker

```bash
git clone https://github.com/Siddharath-Singh16/search_api.git
cd search_api

docker build -t employee-search-api .
docker run -p 8000:8000 employee-search-api
```

### 💻 Option 2: Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload
```

---

## 🌐 API Usage

### `GET /search/employees`

### ✅ Query Parameters:

| Name    | Type   | Required | Description                    |
| ------- | ------ | -------- | ------------------------------ |
| org\_id | string | ✅        | Organization ID (e.g., org1)   |
| search  | string | ❌        | Text search                    |
| status  | string | ❌        | Employee status (e.g., ACTIVE) |
| page    | int    | ❌        | Page number (default = 1)      |
| limit   | int    | ❌        | Page size (default = 10)       |

### 🔄 Response (Dynamic Fields):

```json
[
  {
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering"
  }
]
```

---

## 🔒 Rate Limiting

The API implements a thread-safe rate limiting middleware with the following characteristics:

- **Per-Organization Limiting**: Each organization (identified by `org_id`) has its own rate limit quota
- **Sliding Window Algorithm**: Uses a thread-safe sliding window implementation for accurate rate tracking
- **Configurable Parameters**: 
  - Maximum requests per time window
  - Time window duration in seconds
- **429 Too Many Requests**: Returns HTTP 429 with appropriate headers when rate limit exceeded
- **400 Bad Request**: Returns HTTP 400 if `org_id` is missing in request

Example rate limit configuration (in `main.py`):
```python
# Apply rate limiter middleware with 20 requests per 60 seconds per organization
app.add_middleware(
    RateLimiterMiddleware,
    rate_limit=20,         # Maximum requests
    window_seconds=60      # Time window in seconds
)
```

---

## 🪪 Running Locally

### 1. Clone & Create Environment

```bash
git clone https://github.com/Siddharath-Singh16/search_api.git
cd hr-system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Apply DB Migrations

```bash
alembic upgrade head
```

### 3. Start Server

```bash
uvicorn src.main:app --reload
```

Visit: http://localhost:8000/docs

---

## 💪 Running with Docker

```bash
docker build -t employee-search-api .
docker run -p 8000:8000 employee-search-api
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📊 Org-specific Column Control

Dynamic field inclusion is based on org:

```python
ORG_COLUMN_CONFIG = {
  "org1": ["first_name", "last_name", "department"],
  "org2": ["first_name", "department", "position", "status"]
}
```

Controlled via `src/org_config/column_config.py`.

---

## 🌱 Database Seeding

The database is automatically seeded with test data when the application starts in debug mode. This makes it easy to get started with testing right away.

### Available Test Organizations

For testing purposes, you can use the following organization IDs:

* `org1` - Shows first name, last name, and department columns
* `org2` - Shows first name, department, position, and status columns

Example API call:
```bash
curl "http://localhost:8000/search/employees?org_id=org1"
```

---

## 📜 Migrations

Run migrations via:

```bash
alembic upgrade head
```

---