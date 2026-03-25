#!/bin/bash
set -e

USER_CERT_DIR="/root/certs"
TAILSCALE_CERT_DIR="/root/tailscale"

setup_certs() {
    if [[ -d "${TAILSCALE_CERT_DIR}" && -n "$(ls -A ${TAILSCALE_CERT_DIR}/*.crt 2>/dev/null)" ]]; then
        echo "Tailscale certificates found; setting up HTTPS"
        mkdir -p "${USER_CERT_DIR}"
        cp "${TAILSCALE_CERT_DIR}"/*.crt "${TAILSCALE_CERT_DIR}"/*.key "${USER_CERT_DIR}/"
        chown -R root:root "${USER_CERT_DIR}"
        
        CERT_HOST=$(basename "${TAILSCALE_CERT_DIR}"/*.crt .crt | head -1)
        CERT_PATH="${USER_CERT_DIR}/$(basename "${TAILSCALE_CERT_DIR}"/*.crt)"
        CERT_KEY_PATH="${USER_CERT_DIR}/$(basename "${TAILSCALE_CERT_DIR}"/*.key)"
        
        echo "Using cert: ${CERT_PATH} for host: ${CERT_HOST}"
        exec code-server \
            --bind-addr 0.0.0.0:8080 \
            --cert "${CERT_PATH}" \
            --cert-key "${CERT_KEY_PATH}" \
            --cert-host "${CERT_HOST}" \
            --auth none \
            "$@"
    else
        echo "No Tailscale certificates found; starting plain HTTP"
        exec code-server --bind-addr 0.0.0.0:8080 --auth none "$@"
    fi
}

if [[ $# -gt 0 ]]; then
    exec "$@"
else
    setup_certs
fi
