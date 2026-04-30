# ACEest Fitness and Gym DevOps

Flask API converted from ACEest Tkinter versions with SQLite persistence, CI/CD automation, and test coverage.

## Overview

This API supports:

1. User login (`admin/admin` default user)
2. Program catalog
3. Client management with calorie calculation
4. Membership management
5. Weekly progress tracking
6. Workout logging
7. Metrics and BMI insights
8. AI-style workout plan generation

## Endpoints

1. `POST /auth/login`
2. `GET /`
3. `GET /programs`
4. `GET /programs/<slug>`
5. `GET /clients`
6. `POST /clients`
7. `GET /clients/<name>`
8. `GET /clients/<name>/membership`
9. `PATCH /clients/<name>/membership`
10. `GET /clients/<name>/summary`
11. `GET /clients/<name>/bmi`
12. `GET /clients/export`
13. `POST /progress`
14. `GET /progress/<name>`
15. `GET /progress/<name>/chart`
16. `POST /workouts`
17. `GET /workouts/<name>`
18. `POST /metrics`
19. `GET /metrics/<name>`
20. `GET /metrics/<name>/weight-chart`
21. `POST /ai-program`

## Membership Field Compatibility

The API supports both field names from different Tkinter versions:

1. `membership_expiry` (canonical API field)
2. `membership_end` (alias for compatibility)

You can send either in create/update payloads. Responses include both fields for convenience.

## Local Setup

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python app.py
```

Run tests:

```bash
python -m pytest -q
```

## Sample Requests

### Login

```json
{
  "username": "admin",
  "password": "admin"
}
```

### Create Client

```json
{
  "name": "Asha",
  "age": 28,
  "height": 165,
  "weight": 60,
  "program": "Fat Loss (FL) - 3 day",
  "target_weight": 56,
  "target_adherence": 85,
  "membership_status": "Active",
  "membership_end": "2026-12-31"
}
```

### Update Membership

```json
{
  "membership_status": "Expired",
  "membership_expiry": "2025-12-31"
}
```

### AI Program

```json
{
  "client_name": "Asha",
  "experience": "intermediate"
}
```

## Assignment 2 CI/CD Implementation

This repository contains the Assignment 2 CI/CD implementation for the ACEest Fitness and Gym Flask API. The pipeline uses Jenkins, SonarQube, Docker, GitHub Container Registry, Kubernetes, and Minikube.

The Jenkins pipeline performs:

1. Source code checkout
2. Python dependency installation
3. Unit testing with Pytest
4. Coverage report generation
5. SonarQube code quality analysis
6. SonarQube Quality Gate validation
7. Docker test image build and container test run
8. Docker runtime image build
9. Image push to GitHub Container Registry
10. Kubernetes deployment to Minikube

## CI/CD Tools

1. Jenkins - pipeline automation
2. SonarQube - static code analysis and Quality Gate
3. Docker - application containerization
4. GitHub Container Registry - Docker image registry
5. Kubernetes - container orchestration
6. Minikube - local Kubernetes cluster
7. Pytest - automated unit testing

## Jenkins Pipeline Parameters

The Jenkins pipeline supports parameterized deployments:

| Parameter | Purpose |
| --- | --- |
| `DEPLOYMENT_STRATEGY` | Selects the deployment strategy. Default is `canary`. |
| `BLUE_GREEN_TARGET` | Selects `blue` or `green` for blue-green deployment. |
| `ROLLBACK_TO` | Switches traffic back to `blue` or `green` for rollback. Use `none` for normal builds. |
| `STABLE_REPLICAS` | Stable replica count for canary and A/B deployments. |
| `CANARY_REPLICAS` | Canary or B-variant replica count. |

Supported deployment strategies:

1. `canary`
2. `rolling-update`
3. `blue-green`
4. `shadow`
5. `ab-test`

## SonarQube

SonarQube analysis is configured through `sonar-project.properties`.

The Jenkins pipeline runs the SonarScanner and waits for the SonarQube Quality Gate before building and deploying the Docker image.

For Jenkins Quality Gate callback, configure the SonarQube webhook:

```text
http://<jenkins-host>:<jenkins-port>/sonarqube-webhook/
```

For a local Jenkins setup, use the machine IP address instead of `localhost` or `127.0.0.1`.

## Docker and GitHub Container Registry

The Docker image is built from the project `Dockerfile`.

The pipeline builds:

1. A test image using the `test` target
2. A runtime image using the `runtime` target

The runtime image is pushed to GitHub Container Registry with:

```text
ghcr.io/2024tm93687-star/aceest-fitness-app:<jenkins-build-number>
ghcr.io/2024tm93687-star/aceest-fitness-app:latest
```

## Kubernetes and Minikube

Start Minikube:

```bash
minikube start --driver=docker
```

Check cluster status:

```bash
kubectl get nodes
kubectl get pods
kubectl get svc
```

The pipeline deploys the application to Minikube using Kubernetes manifests from the `k8s/` directory.

## Kubernetes Manifests

The `k8s/` directory contains:

1. `deployment.yaml` - main rolling update deployment
2. `service.yaml` - main NodePort service
3. `deployment-blue.yaml` - blue deployment
4. `deployment-green.yaml` - green deployment
5. `service-blue.yaml` - service selector for blue traffic
6. `service-green.yaml` - service selector for green traffic
7. `deployment-canary.yaml` - canary deployment
8. `deployment-shadow.yaml` - shadow deployment
9. `deployment-ab.yaml` - A/B variant deployment

## Running Deployment Strategies

### Canary

Use Jenkins build parameters:

```text
DEPLOYMENT_STRATEGY = canary
ROLLBACK_TO = none
STABLE_REPLICAS = 3
CANARY_REPLICAS = 1
```

Verify:

```bash
kubectl get deployments
kubectl get pods --show-labels
```

### Rolling Update

Use Jenkins build parameters:

```text
DEPLOYMENT_STRATEGY = rolling-update
ROLLBACK_TO = none
```

Verify:

```bash
kubectl rollout status deployment/aceest-fitness-api
kubectl rollout history deployment/aceest-fitness-api
kubectl get rs
```

### Blue-Green

Deploy green:

```text
DEPLOYMENT_STRATEGY = blue-green
BLUE_GREEN_TARGET = green
ROLLBACK_TO = none
```

Deploy blue:

```text
DEPLOYMENT_STRATEGY = blue-green
BLUE_GREEN_TARGET = blue
ROLLBACK_TO = none
```

Verify:

```bash
kubectl get deployments
kubectl get pods --show-labels
kubectl get svc aceest-fitness-api -o yaml
```

The service selector shows whether traffic is routed to `slot: blue` or `slot: green`.

### Shadow

Use Jenkins build parameters:

```text
DEPLOYMENT_STRATEGY = shadow
ROLLBACK_TO = none
```

Verify:

```bash
kubectl get deployments
kubectl get pods --show-labels
```

### A/B Test

Use Jenkins build parameters:

```text
DEPLOYMENT_STRATEGY = ab-test
ROLLBACK_TO = none
STABLE_REPLICAS = 3
CANARY_REPLICAS = 1
```

Verify:

```bash
kubectl get deployments
kubectl get pods --show-labels
```

## Blue-Green Rollback

To switch traffic back to a previous slot without building a new image, run Jenkins with:

```text
ROLLBACK_TO = blue
```

or:

```text
ROLLBACK_TO = green
```

Verify the service selector:

```bash
kubectl get svc aceest-fitness-api -o yaml
```

## Repository Files

1. `app.py` - main Flask application
2. `requirements.txt` - runtime dependencies
3. `requirements-dev.txt` - development and test dependencies
4. `test_app.py` - Pytest test suite
5. `Dockerfile` - container build definition
6. `Jenkinsfile` - Jenkins CI/CD pipeline
7. `sonar-project.properties` - SonarQube project configuration
8. `k8s/` - Kubernetes deployment and service manifests
9. `README.md` - setup and usage documentation
