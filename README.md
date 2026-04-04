# ACEest Fitness and Gym DevOps

A lightweight Flask API for fitness program data, with CI/CD automation through GitHub Actions and Jenkins.

## Project Overview

This service exposes simple JSON endpoints for fitness programs:

1. `GET /` returns a welcome payload and available routes.
2. `GET /programs` returns all supported program names.
3. `GET /programs/<slug>` returns details for a specific program.

## Tech Stack

1. Python 3
2. Flask
3. Gunicorn
4. Pytest
5. Docker and Docker Compose
6. GitHub Actions
7. Jenkins

## Repository Structure

1. `app.py`: Flask application and API routes
2. `test_app.py`: unit and endpoint tests
3. `requirements.txt`: runtime dependencies
4. `requirements-dev.txt`: runtime plus test dependencies
5. `Dockerfile`: container image definition
6. `docker-compose.yml`: local container orchestration
7. `.github/workflows/main.yml`: GitHub Actions CI pipeline
8. `Jenkinsfile`: Jenkins CI/CD pipeline

## Local Setup and Execution

### Prerequisites

1. Python 3.9+ installed
2. Git installed
3. Docker Desktop installed and running (for container-based run)

### Run Locally with Python Virtual Environment

1. Clone the repository and move into the project folder.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

5. Start the app:

```bash
python app.py
```

6. Open the API:

1. `http://127.0.0.1:5000/`
2. `http://127.0.0.1:5000/programs`

### Run Locally with Docker Compose

1. Build and start:

```bash
docker compose up -d --build
```

2. Verify service:

```bash
docker compose ps
```

3. Open the API:

1. `http://localhost:5000/`
2. `http://localhost:5000/programs`

4. Stop services:

```bash
docker compose down
```

## Manual Test Execution

1. Ensure the virtual environment is active.
2. Install test dependencies if needed:

```bash
python -m pip install -r requirements-dev.txt
```

3. Run tests:

```bash
python -m pytest -q
```

4. Optional verbose run for detailed output:

```bash
python -m pytest test_app.py -v
```

## CI/CD Integration Overview

### GitHub Actions Logic

The GitHub Actions workflow in `.github/workflows/main.yml` runs on:

1. Push events for `feature/*`, `develop`, and `main`
2. Pull requests targeting `develop` and `main`

Pipeline flow:

1. Checkout source code
2. Set up Python 3.9
3. Install dependencies using `requirements-dev.txt`
4. Run tests with `python -m pytest -q`
5. Run static analysis using Ruff
6. Run security checks using Bandit
7. Run dependency vulnerability scan using pip-audit

### Jenkins Pipeline Logic

The Jenkins pipeline in `Jenkinsfile` follows this high-level flow:

1. Checkout source from SCM
2. Create virtual environment and install `requirements-dev.txt`
3. Run test suite from `test_app.py`
4. Build Docker image with two tags:
1. Build-specific tag: `<app-image>:<build-number>`
2. Rolling tag: `<app-image>:latest`
5. Detect normalized branch name from Jenkins environment variables
6. Deploy to DEV when branch is `develop`
7. Deploy to PROD when branch is `main`

Deployment behavior:

1. Existing target container is removed if present
2. New container starts from the current build image
3. DEV maps host port `5001` to container `5000`
4. PROD maps host port `5000` to container `5000`

### Add Pipeline in Jenkins (UI Steps)

Use these steps to create this project pipeline in Jenkins:

1. Open Jenkins dashboard.
2. Select `New Item`.
3. Enter a job name, select `Pipeline`, then click `OK`.
4. In the job configuration page, open `Pipeline` section.
5. Set `Definition` to `Pipeline script from SCM`.
6. Set `SCM` to `Git`.
7. Add repository URL.
8. Add credentials if repository access is private.
9. Set branch specifier (for example `*/develop`, `*/main`, or feature branch).
10. Set `Script Path` to `Jenkinsfile`.
11. Click `Save`.
12. Click `Build Now` to trigger the pipeline.

Optional webhook trigger setup:

1. In Jenkins job, enable `GitHub hook trigger for GITScm polling`.
2. In GitHub repository webhooks, configure payload URL as:

```text
https://<your-jenkins-or-ngrok-url>/github-webhook/
```

### Jenkins Manual Recovery Commands (Inside Jenkins Container)

If your Jenkins job fails with errors such as `python3: not found` or `docker: not found`, you can manually install required tools inside the running Jenkins container.

1. Enter the Jenkins container as root:

```bash
docker exec -u 0 -it <id> bash
```

2. Update package metadata and install Python and Docker CLI package:

```bash
apt-get update && apt-get install -y python3 python3-venv python3-pip docker.io
```

3. Verify installations:

```bash
python3 --version
docker --version
```

4. Exit the container and re-run the Jenkins pipeline.

### Ngrok Setup for GitHub Webhooks to Jenkins

If Jenkins is running locally, ngrok can expose Jenkins to GitHub webhooks.

1. Start ngrok for the Jenkins port (example 8080):

```bash
ngrok http 8080
```

2. Copy the generated HTTPS URL from ngrok.

3. In GitHub repository settings, add or update a webhook:

```text
https://<your-ngrok-id>.ngrok-free.app/github-webhook/
```

4. Set webhook content type to `application/json`.

5. In Jenkins job configuration, enable the GitHub webhook trigger.

6. Keep ngrok running while testing webhook events.

7. If ngrok URL changes, update the webhook payload URL in GitHub.

## Common Commands

Run tests:

```bash
python -m pytest -q
```

Build Docker image:

```bash
docker build -t aceest-fitness-app:latest .
```

Run container:

```bash
docker run --rm -p 5000:5000 aceest-fitness-app:latest
```

## Notes

1. Keep runtime dependencies in `requirements.txt`.
2. Keep test and developer dependencies in `requirements-dev.txt`.
3. Ensure Docker daemon access is configured for Jenkins agents that run Docker stages.
