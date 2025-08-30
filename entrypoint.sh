#!/bin/bash
set -e

if [ "${DEV:-false}" = "true" ]; then
    exec jupyter server \
        --ip=0.0.0.0 \
        --port=8888 \
        --no-browser \
        --IdentityProvider.token= \
        --ServerApp.allow_unauthenticated_access=True \
        --ServerApp.disable_check_xsrf=True \
        --ServerApp.use_redirect_file=False
else
    exec "$@"
fi