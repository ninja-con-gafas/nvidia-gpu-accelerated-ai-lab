#!/bin/bash
set -e

USERNAME=triton-server
AUTH_KEYS="/home/${USERNAME}/.ssh/authorized_keys"
AUTH_KEYS_RO="/home/${USERNAME}/.ssh/authorized_keys_ro"

if [ -f "${AUTH_KEYS_RO}" ]; then
    cp "${AUTH_KEYS_RO}" "${AUTH_KEYS}"
    chown "${USERNAME}:${USERNAME}" "${AUTH_KEYS}"
    chmod u=rw,go= "${AUTH_KEYS}"
fi

if [ "${DEV:-false}" = "true" ]; then
    exec tini -- jupyter server \
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