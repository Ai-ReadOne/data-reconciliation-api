# Data Reconciliation API

## Introduction

**Data Reconciliation API** is a robust and extensible API engine designed to reconcile multiple versions of data across disparate sources. Built using Python and Django, this project provides a scalable and secure foundation for organizations that need to ensure data consistency, integrity, and accuracy in environments where data may be duplicated, fragmented, or updated independently.

Data reconciliation is a critical process in data management, especially in scenarios where data is collected from various systems, departments, or external partners. Inconsistent or conflicting data can lead to reporting errors, compliance issues, and operational inefficiencies.

The project leverages Django’s powerful ORM and REST framework to expose a flexible API for integrating with other systems. It is designed with extensibility in mind, allowing developers to add new reconciliation strategies, data sources, and business logic as requirements evolve.

## Features

- **Automated Data Reconciliation:** Identify and report differences between multiple data versions via background tasks using Celery and Redis.
- **Extensible Architecture:** Easily add new reconciliation rules, data models, and integration points.
- **RESTful API:** Expose reconciliation operations and results via a documented API.
- **Flexible File Storage:** Supports both local file system storage and Google Cloud Storage for uploaded files.
- **OpenAPI Documentation:** Interactive API docs powered by drf-spectacular.
- **Database Agnostic:** Supports PostgreSQL by default, but can be configured for other databases.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python (3.8+ recommended)
- Pip (Python package installer)
- Redis (for Celery message broker and result backend)

## Getting Started

1. **Clone the repository:**

```sh
   git clone https://github.com/ai-readone/data-reconciliation-api.git
   cd data-reconciliation-api
```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Create a `.env` file in the project root directory using samplle from [docs/env_sample](). This file holds your secret keys and configuration settings. You can use the example below as a template.

   ```env
   # .env.example
   # Django Core Settings
   RECONCILIATION_SECRET_KEY=your-strong-secret-key
   RECONCILIATION_DEBUG=True
   RECONCILIATION_ALLOWED_HOSTS=127.0.0.1,localhost
   RECONCILIATION_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

   # Database Settings (PostgreSQL example)
   RECONCILIATION_DATABASE_ENGINE=django.db.backends.postgresql
   RECONCILIATION_DATABASE_NAME=data_reconciliation
   RECONCILIATION_DATABASE_USER=postgres
   RECONCILIATION_DATABASE_PASSWORD=password
   RECONCILIATION_DATABASE_HOST=127.0.0.1
   RECONCILIATION_DATABASE_PORT=5432

   # Celery Settings (using Redis)
   RECONCILIATION_CELERY_BROKER_URL=redis://localhost:6379/0
   RECONCILIATION_CELERY_RESULT_BACKEND=redis://localhost:6379/0

   # File Storage Settings
   # Set to False to use local file storage in the 'media/' directory
   RECONCILIATION_GCLOUD_SUPPORT=False

   # Optional: Google Cloud Storage Settings (only if GCLOUD_SUPPORT is True)
   # RECONCILIATION_GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/gcp-credentials.json
   # RECONCILIATION_GS_BUCKET_NAME=your-gcs-bucket-name
   ```
5. **Run database migrations:**

   ```sh
   python manage.py migrate
   ```
6. **Run the development server:**

   ```sh
   unvicorn data_reconciliation_api.asgi:application --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://127.0.0.1:8000`.
7. **Run the Celery worker:**
   In a separate terminal, start the Celery worker to process background reconciliation tasks. Make sure your Redis server is running.

   ```sh
   celery -A data_reconciliation_api worker -l info
   ```

## Running with Docker

This project is fully containerized using Docker and Docker Compose, which is the recommended way to run it for development.

1. **Prerequisites:**

   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)
2. **Configure Environment:**
   Create a `.env` file in the project root. You can copy `docs/env_sample` and modify it. For Docker, ensure your database and Redis hosts point to the service names defined in `docker-compose.yml`.

   ```env
   # .env for Docker
   # ... other settings ...

   # Database host is the service name in docker-compose.yml
   RECONCILIATION_DATABASE_HOST=db

   # Celery broker and result backend host is the service name
   RECONCILIATION_CELERY_BROKER_URL=redis://redis:6379/0
   RECONCILIATION_CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```
3. **Build and Run:**
   From the project root directory, run:

   ```sh
   docker-compose up --build or docker compose up ---build
   ```

   This command will build the Docker image, start all services (web, db, redis, worker), and apply database migrations automatically. The API will be available at `http://localhost:8000`.
4. **Stopping the application:**
   To stop the containers, press `Ctrl+C` or run `docker-compose down` from another terminal.

## Configuration

### File Storage

The project supports two modes for storing uploaded CSV files, controlled by the `RECONCILIATION_GCLOUD_SUPPORT` environment variable:

- **Local Storage (Default):** When `RECONCILIATION_GCLOUD_SUPPORT` is set to `False`, files are stored locally in the `media/` directory at the project root. This is the default behavior if the variable is not set.
- **Google Cloud Storage (Optional):** To use GCS, set `RECONCILIATION_GCLOUD_SUPPORT` to `True`. You must also provide your GCP credentials path and bucket name via the `RECONCILIATION_GOOGLE_APPLICATION_CREDENTIALS` and `RECONCILIATION_GS_BUCKET_NAME` environment variables.

## API Documentation and Endpoints

This project uses `drf-spectacular` to automatically generate OpenAPI 3 documentation for the API. This provides interactive documentation where you can explore and test the API endpoints directly from your browser.

Once the application is running (either locally or via Docker), you can access the documentation at the following URLs:

- **Swagger UI:** `http://localhost:8000/api/v1/schema/swagger-ui/`
- **ReDoc:** `http://localhost:8000/api/v1/schema/redoc/`
- **Schema (YAML):** `http://localhost:8000/api/v1/schema/`

### Endpoints Summary

All endpoints are available under the base path `/api/v1/reconciliations/csv`.

#### `POST /`

Starts a new data reconciliation job.

- **Method:** `POST`
- **Description:** Uploads a source and a target CSV file for reconciliation. The request must be `multipart/form-data`.
- **Request Body:**
  - `source_file` (file): The source CSV file.
  - `target_file` (file): The target CSV file.
  - `unique_fields` (string): A comma-separated list of column names to uniquely identify rows (e.g., "id,email").
- **Success Response:** `202 Accepted` with the details of the newly created job, including its `job_id` and initial `status` ("processing").

#### `GET /`

Lists all submitted reconciliation jobs.

- **Method:** `GET`
- **Description:** Retrieves a paginated list of all reconciliation jobs.
- **Success Response:** `200 OK` with a list of jobs, each containing `id`, `created_at`, `updated_at`, and `status`.

#### `GET /{job_id}/json/`

Retrieves the status and result of a specific job in JSON format.

- **Method:** `GET`
- **Description:** Fetches the details of a single reconciliation job by its UUID. If the job is `completed`, the response body will contain the reconciliation report as a JSON object.
- **URL Params:**
  - `job_id` (uuid): The ID of the job to retrieve.
- **Success Response:** `200 OK` with the job status or the full JSON report.

#### `GET /{job_id}/csv/`

Downloads the reconciliation report for a specific job in CSV format.

- **Method:** `GET`
- **Description:** Generates and returns a reconciliation report as a CSV file attachment. This endpoint is only useful for jobs with a `completed` status.
- **URL Params:**
  - `job_id` (uuid): The ID of the job.
- **Success Response:** `200 OK` with `Content-Type: text/csv`.

#### `GET /{job_id}/html/`

Views the reconciliation report for a specific job as an HTML page.

- **Method:** `GET`
- **Description:** Generates and returns a reconciliation report as an HTML page. This endpoint is only useful for jobs with a `completed` status.
- **URL Params:**
  - `job_id` (uuid): The ID of the job.
- **Success Response:** `200 OK` with `Content-Type: text/html`.
