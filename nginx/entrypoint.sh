#!/usr/bin/env bash

# This entrypoint allows using nginx template with Docker and placing variables in runtime

# Substitute env vars in template -> final nginx config
envsubst "${SHALLWE_GLOBAL_SITE_URL_INTERNAL} ${NEXT_PUBLIC_SHALLWE_API_BASE_URL_INTERNAL}" \
  < /etc/nginx/templates/nginx.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"  # Prevent nginx from detaching
