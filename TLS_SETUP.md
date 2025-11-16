# TLS & Certificate Management

HTTPS is now handled inside Docker with Nginx terminating TLS. Certificates
live under `certbot/` (ignored by Git) and are mounted into both the `nginx`
and `certbot` containers.

## 1. Bootstrap (first time only)

1. Define the email used for Let’s Encrypt in your shell or `.env`:
   ```bash
   export CERTBOT_EMAIL="you@example.com"
   export CERTBOT_DOMAIN="bricolle-family.fr"  # optional, defaults to this value
   ```
2. Initiate certificate issuance (the script automatically removes any old
   placeholder/self-signed files and creates temporary ones for nginx if
   needed):
   ```bash
   ./scripts/manage_certs.sh init
   ```
3. Deploy the stack: `./deploy.sh`
4. (Optional) rerun `./scripts/manage_certs.sh init` if you change domains.
   ```bash
   ./scripts/manage_certs.sh init
   ```
   The command runs Certbot in webroot mode and reloads Nginx when done.

## 2. Renewal

- `./scripts/manage_certs.sh renew` checks all certificates and reloads Nginx
  if anything changed. `deploy.sh` already calls this at the end of every
  deploy, but you can also add a cron entry (e.g. twice per day):
  ```cron
  0 3,15 * * * /home/ubuntu/Custom_projects/bricolle-family/scripts/manage_certs.sh renew >> /var/log/certbot-renew.log 2>&1
  ```

## 3. Manual health check

After deploying, confirm HTTPS works end-to-end:

```bash
TOKEN="your-token-here"
curl -H "X-MCP-TOKEN: ${TOKEN}" https://bricolle-family.fr/flash_cards/api/categories/
```

You should receive the JSON payload with categories. If `curl` fails, inspect
the containers with `docker compose logs nginx` and re-run the bootstrap/init
commands as needed.
