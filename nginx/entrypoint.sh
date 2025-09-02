#!/usr/bin/env bash

# This entrypoint allows using nginx template with Docker and placing variables in runtime

# Define template and out paths
TEMPLATE="/etc/nginx/templates/default.conf.template"
OUT="/etc/nginx/conf.d/default.conf"

# Check for template
if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: template not found: $TEMPLATE" >&2
  exit 1
fi

# Substitute env vars in template -> final nginx config (single quotes exactly to pass var names, not values)
envsubst '$SHALLWE_GLOBAL_SITE_URL_INTERNAL $NEXT_PUBLIC_SHALLWE_API_BASE_URL_INTERNAL' \
  < "$TEMPLATE" \
  > "$OUT"

exec nginx -g "daemon off;"  # Prevent nginx from detaching
