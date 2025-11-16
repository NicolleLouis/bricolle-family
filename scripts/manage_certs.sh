#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

COMMAND="${1:-renew}"
DOMAIN="${CERTBOT_DOMAIN:-bricolle-family.fr}"
EMAIL="${CERTBOT_EMAIL:-}"
LE_DIR="${PROJECT_ROOT}/certbot/letsencrypt"
WEBROOT_DIR="${PROJECT_ROOT}/certbot/www"
LIVE_DIR="${LE_DIR}/live/${DOMAIN}"
FULLCHAIN_PATH="${LIVE_DIR}/fullchain.pem"
PRIVKEY_PATH="${LIVE_DIR}/privkey.pem"

mkdir -p "${LE_DIR}" "${WEBROOT_DIR}"

ensure_bootstrap_cert() {
    if [[ -f "${FULLCHAIN_PATH}" && -f "${PRIVKEY_PATH}" ]]; then
        return
    fi

    echo "🔐 Generating temporary self-signed certificate for ${DOMAIN}..."
    mkdir -p "${LIVE_DIR}"
    openssl req -x509 -nodes -newkey rsa:2048 \
        -subj "/CN=${DOMAIN}" \
        -keyout "${PRIVKEY_PATH}" \
        -out "${FULLCHAIN_PATH}" \
        -days 30 >/dev/null 2>&1
}

cleanup_legacy_cert() {
    if [[ -d "${LE_DIR}/live/${DOMAIN}" || -d "${LE_DIR}/archive/${DOMAIN}" ]]; then
        echo "🧹 Removing previous certificate material for ${DOMAIN}..."
        rm -rf \
            "${LE_DIR}/live/${DOMAIN}" \
            "${LE_DIR}/archive/${DOMAIN}" \
            "${LE_DIR}/renewal/${DOMAIN}.conf" \
            "${LE_DIR}/renewal/${DOMAIN//./_}.conf" \
            "${LE_DIR}/csr" \
            "${LE_DIR}/keys"
        mkdir -p "${LE_DIR}/renewal"
    fi
}

reload_nginx() {
    docker compose exec nginx nginx -s reload >/dev/null 2>&1 || true
}

case "${COMMAND}" in
    bootstrap)
        ensure_bootstrap_cert
        echo "✅ Bootstrap certificate ready at ${LIVE_DIR}."
        ;;
    init)
        cleanup_legacy_cert
        if [[ -z "${EMAIL}" ]]; then
            echo "❌ Set CERTBOT_EMAIL before running init."
            exit 1
        fi
        echo "📜 Requesting Let's Encrypt certificate for ${DOMAIN}..."
        docker compose run --rm certbot certonly \
            --webroot -w /var/www/certbot \
            --agree-tos --no-eff-email \
            --email "${EMAIL}" \
            --force-renewal \
            -d "${DOMAIN}" -d "www.${DOMAIN}"
        reload_nginx
        echo "✅ Certificate issued and nginx reloaded."
        ;;
    renew)
        echo "♻️  Renewing certificates (if needed)..."
        docker compose run --rm certbot renew
        reload_nginx
        echo "✅ Renewal check complete."
        ;;
    *)
        echo "Usage: $0 [bootstrap|init|renew]"
        exit 1
        ;;
esac
