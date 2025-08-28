# syntax=docker/dockerfile:1

FROM nginx:alpine

# Install envsubst (part of gettext for using template env vars)
RUN apk add --no-cache gettext

# Copy template and entrypoint (for variable placement)
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
