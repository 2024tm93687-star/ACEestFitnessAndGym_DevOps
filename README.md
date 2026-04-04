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
7. `GET /clients/export` downloads client records as CSV.
8. `POST /progress` saves weekly adherence progress.
9. `GET /progress/<name>` fetches progress history for a client.
10. `GET /progress/<name>/chart` returns chart-ready progress arrays (weeks and adherence).
11. `GET /clients/<name>/summary` returns profile + goals + progress summary + latest metrics.
12. `GET /clients/<name>/bmi` returns BMI category and risk note.
13. `POST /workouts` logs workout sessions (with optional exercises).
14. `GET /workouts/<name>` returns workout history.
15. `POST /metrics` logs body metrics.
16. `GET /metrics/<name>` returns metric history.
17. `GET /metrics/<name>/weight-chart` returns chart-ready weight trend data.

The current API content is based on the latest ACEest Tkinter desktop version (v2.2.4) and has been converted into a Flask-based service for API and DevOps workflows, including SQLite persistence.

## Tech Stack

1. Python 3
2. Flask
3. Gunicorn
4. SQLite3
5. Pytest
6. Docker and Docker Compose
7. GitHub Actions
8. Jenkins

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
6. `factor`
7. `calorie_factor` (backward-compatible alias)
8. `desc`

Example program slugs:

1. `fat-loss-fl-3-day`
2. `fat-loss-fl-5-day`
3. `muscle-gain-mg-ppl`
3. `beginner-bg`

Sample response for `GET /programs/fat-loss-fl-3-day`:

```json
{
	"factor": 22,
	"calorie_factor": 22,
	"color": "#e74c3c",
	"desc": "3-day full-body fat loss",
	"diet": "Egg Whites, Chicken, Fish Curry",
	"name": "Fat Loss (FL) - 3 day",
	"slug": "fat-loss-fl-3-day",
	"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery"
}
```

Sample request for `POST /clients`:

```json
{
	"name": "Asha",
	"age": 28,
	"height": 165,
	"weight": 60,
	"program": "Fat Loss (FL) - 3 day",
	"target_weight": 56,
	"target_adherence": 85
}
```

Sample response for `POST /clients`:

```json
{
	"message": "Client Asha saved successfully.",
	"client": {
		"name": "Asha",
		"age": 28,
		"height": 165.0,
		"weight": 60.0,
		"program": "Fat Loss (FL) - 3 day",
		"calories": 1320,
		"target_weight": 56.0,
		"target_adherence": 85
	}
}
```

Sample response for `GET /clients/Asha`:

```json
{
	"name": "Asha",
	"age": 28,
	"height": 165.0,
	"weight": 60.0,
	"program": "Fat Loss (FL) - 3 day",
	"calories": 1320,
	"target_weight": 56.0,
	"target_adherence": 85
}
```

Sample response for `GET /clients`:

```json
{
	"clients": [
		{
			"name": "Asha",
			"age": 28,
			"height": 165.0,
			"weight": 60.0,
			"program": "Fat Loss (FL) - 3 day",
			"calories": 1320,
			"target_weight": 56.0,
			"target_adherence": 85
		}
	],
	"count": 1
}
```

Sample response headers for `GET /clients/export`:

1. Content-Type: `text/csv`
2. Content-Disposition: `attachment; filename=clients.csv`

Sample response for `GET /clients/Asha/summary`:

```json
{
	"client": {
		"name": "Asha",
		"age": 28,
		"height": 165.0,
		"weight": 60.0,
		"program": "Fat Loss (FL) - 3 day",
		"calories": 1320,
		"target_weight": 56.0,
		"target_adherence": 85
	},
	"program_desc": "3-day full-body fat loss",
	"progress_summary": {
		"weeks_logged": 2,
		"average_adherence": 82.5
	},
	"last_metric": {
		"date": "2026-04-04",
		"weight": 60.0,
		"waist": 76.0,
		"bodyfat": 22.0
	}
}
```

Sample response for `GET /clients/Asha/bmi`:

```json
{
	"client_name": "Asha",
	"bmi": 22.0,
	"category": "Normal",
	"risk": "Low risk if active and strong."
}
```

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

Sample response for `GET /progress/Asha/chart`:

```json
{
	"client_name": "Asha",
	"weeks": ["Week 01 - 2026", "Week 02 - 2026"],
	"adherence": [90, 75]
}
```

Sample request for `POST /workouts`:

```json
{
	"client_name": "Asha",
	"date": "2026-04-04",
	"workout_type": "Strength",
	"duration_min": 60,
	"notes": "Good session",
	"exercises": [
		{
			"name": "Squat",
			"sets": 3,
			"reps": 5,
			"weight": 80
		}
	]
}
```

Sample response for `GET /workouts/Asha`:

```json
{
	"workouts": [
		{
			"id": 1,
			"date": "2026-04-04",
			"workout_type": "Strength",
			"duration_min": 60,
			"notes": "Good session"
		}
	],
	"count": 1
}
```

Sample request for `POST /metrics`:

```json
{
	"client_name": "Asha",
	"date": "2026-04-04",
	"weight": 60.0,
	"waist": 76.0,
	"bodyfat": 22.0
}
```

Sample response for `GET /metrics/Asha/weight-chart`:

```json
{
	"client_name": "Asha",
	"dates": ["2026-04-04", "2026-04-11"],
	"weights": [60.0, 59.2]
}
```

## CI/CD Integration Overview

### GitHub Actions Logic
# ACEest Fitness and Gym DevOps

A Flask API converted from ACEest Tkinter v3.0.1 for client management, progress tracking, workout logging, body metrics, and analytics.

## Project Overview

The API provides:

1. Program definitions with calorie factors and descriptions.
2. Persistent client profiles with goals.
3. Weekly adherence tracking and chart-ready data.
4. Workout logging with optional exercise entries.
5. Body metrics logging (weight, waist, bodyfat).
6. BMI and risk insight endpoint.

## Main Endpoints

1. `GET /`
2. `GET /programs`
3. `GET /programs/<slug>`
4. `GET /clients`
5. `POST /clients`
6. `GET /clients/<name>`
7. `GET /clients/<name>/summary`
8. `GET /clients/<name>/bmi`
9. `GET /clients/export`
10. `POST /progress`
11. `GET /progress/<name>`
12. `GET /progress/<name>/chart`
13. `POST /workouts`
14. `GET /workouts/<name>`
15. `POST /metrics`
16. `GET /metrics/<name>`
17. `GET /metrics/<name>/weight-chart`

## Tech Stack

1. Python 3
2. Flask
3. SQLite3
4. Pytest
5. Docker and Docker Compose
6. GitHub Actions
7. Jenkins

## Local Setup

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python app.py
```

App URL:

1. `http://127.0.0.1:5000/`

## Database

1. Default DB file: `aceest_fitness.db`
2. Override via env var: `ACEEST_DB_NAME`

PowerShell example:

```powershell
$env:ACEEST_DB_NAME = "aceest_fitness.db"
python app.py
```

## Program Slugs

1. `fat-loss-fl-3-day`
2. `fat-loss-fl-5-day`
3. `muscle-gain-mg-ppl`
4. `beginner-bg`

## API Samples

Sample `GET /programs/fat-loss-fl-3-day`:

```json
{
	"name": "Fat Loss (FL) - 3 day",
	"slug": "fat-loss-fl-3-day",
	"desc": "3-day full-body fat loss",
	"factor": 22,
	"calorie_factor": 22,
	"color": "#e74c3c",
	"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
	"diet": "Egg Whites, Chicken, Fish Curry"
}
```

Sample `POST /clients` request:

```json
{
	"name": "Asha",
	"age": 28,
	"height": 165,
	"weight": 60,
	"program": "Fat Loss (FL) - 3 day",
	"target_weight": 56,
	"target_adherence": 85
}
```

Sample `GET /clients/Asha/summary` response:

```json
{
	"client": {
		"name": "Asha",
		"age": 28,
		"height": 165.0,
		"weight": 60.0,
		"program": "Fat Loss (FL) - 3 day",
		"calories": 1320,
		"target_weight": 56.0,
		"target_adherence": 85
	},
	"program_desc": "3-day full-body fat loss",
	"progress_summary": {
		"weeks_logged": 2,
		"average_adherence": 82.5
	},
	"last_metric": {
		"date": "2026-04-04",
		"weight": 60.0,
		"waist": 76.0,
		"bodyfat": 22.0
	}
}
```

Sample `GET /clients/Asha/bmi` response:

```json
{
	"client_name": "Asha",
	"bmi": 22.0,
	"category": "Normal",
	"risk": "Low risk if active and strong."
}
```

Sample `POST /workouts` request:

```json
{
	"client_name": "Asha",
	"date": "2026-04-04",
	"workout_type": "Strength",
	"duration_min": 60,
	"notes": "Good session",
	"exercises": [
		{
			"name": "Squat",
			"sets": 3,
			"reps": 5,
			"weight": 80
		}
	]
}
```

Sample `POST /metrics` request:

```json
{
	"client_name": "Asha",
	"date": "2026-04-04",
	"weight": 60.0,
	"waist": 76.0,
	"bodyfat": 22.0
}
```

Sample `GET /metrics/Asha/weight-chart` response:

```json
{
	"client_name": "Asha",
	"dates": ["2026-04-04", "2026-04-11"],
	"weights": [60.0, 59.2]
}
```

## Tests

```bash
python -m pytest -q
```

## CI/CD

1. GitHub Actions workflow: `.github/workflows/main.yml`
2. Jenkins pipeline: `Jenkinsfile`
