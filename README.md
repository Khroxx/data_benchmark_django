# Data Benchmark Django

Django backend for the benchmark comparison project. It provides a simple benchmark API compatible with the frontend and the other backend implementations.

## Clone

SSH:

```bash
git clone git@github.com:Khroxx/data_benchmark_django.git
```

HTTPS:

```bash
git clone https://github.com/Khroxx/data_benchmark_django.git
```

## Endpoints

- `GET /ping`
- `GET /api/django/benchmark`

Supported query params:

- `type=flat-json | nested-json | csv | blob`
- `size` or `sizeKb`
- `runs`

## Local development

Create a virtual environment:

```bash
python3 -m venv .venv
```

Install dependencies:

```bash
./.venv/bin/pip install -r requirements.txt
```

Start the server:

```bash
./.venv/bin/python manage.py runserver 0.0.0.0:8080
```

Run the Django project check:

```bash
./.venv/bin/python manage.py check
```
