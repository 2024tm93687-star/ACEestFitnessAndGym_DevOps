# ACEest Fitness and Gym DevOps

A lightweight Flask API for fitness program and client management data, with CI/CD automation through GitHub Actions and Jenkins.

## Project Overview

This service exposes simple JSON endpoints for fitness programs:

1. `GET /` returns a welcome payload and available routes.
2. `GET /programs` returns all supported program names.
3. `GET /programs/<slug>` returns details for a specific program, including workout plan, nutrition plan, display color, and calorie factor.
4. `GET /clients` returns saved client records.
5. `POST /clients` saves or updates a client record and calculates calories.
6. `GET /clients/<name>` loads one client by name.
6. `GET /clients/export` downloads client records as CSV.
7. `POST /progress` saves weekly adherence progress.
8. `GET /progress/<name>` fetches progress history for a client.

The current API content is based on the latest ACEest Tkinter desktop version and has been converted into a Flask-based service for API and DevOps workflows, including SQLite persistence.

## Tech Stack

1. Python 3
2. Flask
3. Gunicorn
4. SQLite3
5. Pytest
5. Docker and Docker Compose
6. GitHub Actions
7. Jenkins

## Repository Structure

1. `app.py`: Flask application and API routes
2. `test_app.py`: unit and endpoint tests
3. `requirements.txt`: runtime dependencies
4. `requirements-dev.txt`: runtime plus test dependencies
5. `aceest_fitness.db`: SQLite database file (auto-created at runtime)
6. `Dockerfile`: container image definition
7. `docker-compose.yml`: local container orchestration
8. `.github/workflows/main.yml`: GitHub Actions CI pipeline
9. `Jenkinsfile`: Jenkins CI/CD pipeline

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
3. `http://127.0.0.1:5000/programs/fat-loss-fl`

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
3. `http://localhost:5000/programs/muscle-gain-mg`

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

## Database Persistence

Client and progress data are persisted in SQLite.

1. Default database file: `aceest_fitness.db`
2. Override with environment variable: `ACEEST_DB_NAME`

Example (PowerShell):

```powershell
$env:ACEEST_DB_NAME = "aceest_fitness.db"
python app.py
```

## API Response Overview

Each program detail response includes:

1. `name`
2. `slug`
3. `workout`
4. `diet`
5. `color`
6. `calorie_factor`

Example program slugs:

1. `fat-loss-fl`
2. `muscle-gain-mg`
3. `beginner-bg`

Sample response for `GET /programs/fat-loss-fl`:

```json
{
	"calorie_factor": 22,
	"color": "#e74c3c",
	"diet": "Egg Whites, Chicken, Fish Curry",
	"name": "Fat Loss (FL)",
	"slug": "fat-loss-fl",
	"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery"
}
```

Sample request for `POST /clients`:

```json
{
	"name": "Asha",
	"age": 28,
	"weight": 60,
	"program": "Fat Loss (FL)"
}
```

Sample response for `POST /clients`:

```json
{
	"message": "Client Asha saved successfully.",
	"client": {
		"name": "Asha",
		"age": 28,
		"weight": 60.0,
		"program": "Fat Loss (FL)",
		"calories": 1320
	}
}
```

Sample response for `GET /clients/Asha`:

```json
{
	"name": "Asha",
	"age": 28,
	"weight": 60.0,
	"program": "Fat Loss (FL)",
	"calories": 1320
}
```

Sample response for `GET /clients`:

```json
{
	"clients": [
		{
			"name": "Asha",
			"age": 28,
			"weight": 60.0,
			"program": "Fat Loss (FL)",
			"calories": 1320
		}
	],
	"count": 1
}
```

Sample response headers for `GET /clients/export`:

1. Content-Type: `text/csv`
2. Content-Disposition: `attachment; filename=clients.csv`

Sample request for `POST /progress`:

```json
{
	"name": "Asha",
	"adherence": 90,
	"week": "Week 01 - 2026"
}
```

Sample response for `POST /progress`:

```json
{
	"message": "Weekly progress logged",
	"progress": {
		"client_name": "Asha",
		"week": "Week 01 - 2026",
		"adherence": 90
	}
}
```

Sample response for `GET /progress/Asha`:

```json
{
	"progress": [
		{
			"client_name": "Asha",
			"week": "Week 01 - 2026",
			"adherence": 90
		}
	],
	"count": 1
}
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
