# 🧾 Employee Search Microservice

A high-performance, configurable microservice for an HR company to search employees across millions of records efficiently, with per-organization column visibility and built-in rate limiting. Built using **FastAPI**, **SQLite**, and Python's **standard library only**.

---

## 🚀 Features

- 🔎 **Search API** for employee directory
- 🏢 **Dynamic columns per organization** (configurable output fields)
- ⚡ **Efficient pagination & filtering**
- 🛡 **In-memory rate limiting** (no 3rd-party lib used)
- 🧪 **Unit tested** using `pytest`
- 📦 **Containerized** via Docker
- 📄 **OpenAPI compliant**

---

## 📁 Folder Structure

```
hr_system/
├── src/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── rate_limiter.py
|   |   └──config.json
│   ├── db/
│   │   ├── sqlite.py
│   └── main.py
├── tests/
    ├──conftest.py
│   ├── test_api.py
│   └── test_rate_limiter.py
├
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🧑‍💻 Getting Started

### 🐳 Option 1: Docker

```bash
git clone https://github.com/Siddharath-Singh16/employee-search-api.git
cd employee-search-api

docker build -t employee-search-api .
docker run -p 8000:8000 employee-search-api
```

### 💻 Option 2: Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn src.main:app --reload
```

---

## 🌐 API Usage

### `GET /search/employees`

Search for employees within an organization.

#### Query Parameters

| Param     | Type   | Description                         |
|-----------|--------|-------------------------------------|
| `org_id`  | string | **Required**. Organization ID       |
| `search`  | string | Search term (name, position, etc)   |
| `status`  | string | Filter by status (e.g., active)     |
| `page`    | int    | Page number (default 1)             |
| `limit`   | int    | Page size (default 10)              |

#### Example

```bash
curl "http://localhost:8000/search/employees?org_id=org1&search=engineer&page=1&limit=10"
```

#### Sample Response

```json
[
  {
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering",
    "position": "Developer"
  }
]
```

---

## 🧠 Organization Configuration

Dynamic fields are defined in `org_config.json`. Example:

```json
{
  "org1": ["first_name", "last_name", "department", "position"],
  "org2": ["first_name", "location", "status"]
}
```

---

## 📊 Rate Limiting

- **20 requests/minute per organization**
- Implemented using `collections.deque` (no third-party libraries)
- Error response:

```json
{
  "detail": "Rate limit exceeded"
}
```

---

## 🧪 Running Tests

```bash
export PYTHONPATH=.
pytest
```

Test coverage includes:
- ✅ API functionality
- ✅ Rate limiter logic
- ✅ Edge cases

---

## 📦 OpenAPI Docs

Once the server is running, visit:

- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- JSON schema: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---


## 📌 Notes

- DB is seeded at startup.
- Designed for containerized deployment.
- Ready for enterprise scaling with persistent RDBMS (e.g., PostgreSQL).

---
