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

## Environment

This repo is configured for public local testing. The default values are development-only and can be committed safely for this benchmark project.

Public example env file:

```bash
cp .env.example .env
```

Current public variables:

- `DJANGO_SECRET_KEY=public-dev-only-benchmark-secret-key`
- `DJANGO_DEBUG=true`
- `DJANGO_ALLOWED_HOSTS=*`
- `CORS_ALLOWED_ORIGIN=*`
- `CORS_ALLOWED_METHODS=GET, OPTIONS`
- `CORS_ALLOWED_HEADERS=Content-Type, Authorization`

The Django settings load `.env` automatically before reading those values.

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
