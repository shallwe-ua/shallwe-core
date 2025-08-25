# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10.18
FROM python:${PYTHON_VERSION}-slim

# Prevent Python stdout/stderr buffering
ENV PYTHONUNBUFFERED=1
# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install libGL for AI usage
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install poetry using pip and configure it
RUN --mount=type=cache,target=/root/.cache \
    pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

# Copy dependency lists
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .
