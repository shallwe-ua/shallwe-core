#!/usr/bin/env bash

# Entrypoint that allows to switch between automatic/manual Django-wise build and run in dev/qa
# Also prevents from exiting if manual termination of server happens in dev/qa

MANAGEPY="python3 manage.py"


switch_to_idle() {
  echo "[entrypoint] Django server not running; falling back to sleep infinity; start manually"
  exec sleep infinity
}


if [ "${SHALLWE_BACKEND_ENTRYPOINT_AUTORUN}" = "true" ]; then

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

  # [Attention] Trap SIGINT and SIGTERM while runserver is running
  # shellcheck disable=SC3048
  trap switch_to_idle SIGINT SIGTERM

  echo "[entrypoint] Starting dev server..."
  $MANAGEPY runserver 0.0.0.0:8000

  # If runserver exits normally, fall back to idle
  switch_to_idle
else
  switch_to_idle
fi
