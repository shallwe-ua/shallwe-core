#!/usr/bin/env bash

# Entrypoint that allows to switch between automatic/manual Django-wise build and run in dev/qa
# Also prevents from exiting if manual termination of server happens in dev/qa

MANAGEPY="python3 manage.py"


prepare_backend() {
  # Prepare config variables
  python3 ./shallwe_core/envconfig/parse_to_constants.py

  # Run tests if autotest active
  if [ "${SHALLWE_BACKEND_ENTRYPOINT_AUTOTEST}" = "true" ]; then
    $MANAGEPY test --noinput -v 2
  fi

  # Prepare database schema
  $MANAGEPY migrate

  # Populate locations
  $MANAGEPY update_locations

  # Create superuser if not exists
  if $MANAGEPY createsuperuser --no-input; then
    echo "[entrypoint] ✅ Superuser created"
  else
    echo "[entrypoint] ⚠ Superuser not created — already exists or something else went wrong. Skipping"
  fi

  # Collect static files if not dev
  if [ "${HSALLWE_GLOBAL_ENV_MODE}" != "DEV" ]; then
    $MANAGEPY collectstatic --noinput
  fi
}


switch_to_idle() {
  echo "[entrypoint] Django server not running; falling back to sleep infinity; start manually"
  exec sleep infinity
}


run_dev_server() {
  # [Attention] Trap SIGINT and SIGTERM while runserver is running
  trap switch_to_idle SIGINT SIGTERM

  echo "[entrypoint] Starting Django dev server..."
  $MANAGEPY runserver 0.0.0.0:8000 --insecure  # Insecure flag in DEV ensures serving static by Django even if DEBUG=False

  # If runserver exits normally, fall back to idle
  switch_to_idle
}


run_qa_server() {
  echo "[entrypoint] Starting QA server with Gunicorn..."

  # Get desired workers count
  CPU_CORES_COUNT=$(getconf _NPROCESSORS_ONLN)
  WORKERS_COUNT=$((SHALLWE_BACKEND_ENTRYPOINT_WORKERS_MULT * CPU_CORES_COUNT + 1))
  echo "[entrypoint] Using $WORKERS_COUNT Gunicorn workers"

  # Use or not preload
  PRELOAD_ARG=""
  if [ "$SHALLWE_BACKEND_ENTRYPOINT_WORKERS_PRELOAD" = "true" ]; then
    PRELOAD_ARG="--preload"
  fi

  # Timeout setting
  TIMEOUT_ARG=""
  if [ -n "$SHALLWE_BACKEND_ENTRYPOINT_WORKERS_TIMEOUT" ]; then
    TIMEOUT_ARG="--timeout $SHALLWE_BACKEND_ENTRYPOINT_WORKERS_TIMEOUT"
  else
    TIMEOUT_ARG="--timeout 30"  # Default gunicorn timeout
  fi

  # Gunicorn replaces the shell; assuming static/media served externally
  exec gunicorn shallwe_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS_COUNT" \
    --log-level info \
    --capture-output \
    --forwarded-allow-ips="*" \
    $PRELOAD_ARG \
    "$TIMEOUT_ARG"
}


run_server() {
  if [ "$SHALLWE_GLOBAL_ENV_MODE" = "DEV" ]; then
    run_dev_server
  elif [ "$SHALLWE_GLOBAL_ENV_MODE" = "QA" ]; then
    run_qa_server
  else
    echo "[entrypoint] ⚠ Unknown environment mode: $SHALLWE_GLOBAL_ENV_MODE"
    switch_to_idle
  fi
}


if [ "${SHALLWE_BACKEND_ENTRYPOINT_AUTORUN}" = "true" ]; then
  prepare_backend
  run_server
else
  switch_to_idle
fi
