FROM python:3.12-slim
# Size: use the slim Python base image to reduce final image footprint.

# Security: disable .pyc generation and force unbuffered logs for predictable runtime behavior.
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# Security: create a dedicated non-root user so the app does not run as root inside the container.
RUN groupadd --system app && useradd --system --gid app app

COPY requirements.txt .
# Runtime image installs only production dependencies.
# Test tools (for example pytest) are intentionally excluded and installed in CI via requirements-dev.txt.
# Size: install dependencies before copying app code to maximize Docker layer cache reuse.
RUN pip install --upgrade pip && pip install -r requirements.txt

# Security/Size: copy only runtime application code (avoid shipping tests/docs/secrets by default).
COPY app.py .

# Security: ensure app user owns runtime files before dropping privileges.
RUN chown -R app:app /app

# Security: run the service as a non-root user.
USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]