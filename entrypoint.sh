#!/bin/bash
set -e

if [[ $# -gt 0 ]]; then
    exec "$@"
else
    exec jupyter server \
        --ip=0.0.0.0 \
        --port=8888 \
        --no-browser \
        --IdentityProvider.token="${JUPYTER_TOKEN:-}" \
        --ServerApp.allow_unauthenticated_access="${JUPYTER_ALLOW_UNAUTHENTICATED_ACCESS:-False}" \
        --ServerApp.disable_check_xsrf="${JUPYTER_DISABLE_CHECK_XSRF:-False}" \
        --ServerApp.use_redirect_file="${JUPYTER_USE_REDIRECT_FILE:-False}" \
        ${JUPYTER_ARGS:-}
fi
