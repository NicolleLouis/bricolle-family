# Production 502 Troubleshooting

## Symptoms
- Nginx returned `502 Bad Gateway` for all requests, including `/favicon.ico`.
- Nginx logs showed `connect() failed (113: No route to host) while connecting to upstream "http://172.18.0.4:8000"`.
- `docker compose ps` revealed the `nginx` container was healthy, but it had lost connectivity to the `web` container.

## Root Cause
Nginx caches the upstream IP (`172.18.0.4`) and occasionally loses the route after a container restart. When Gunicorn is restarted or the Docker network changes, nginx still targets the old IP and fails with `No route to host`.

## Resolution
1. Restart only nginx so it refreshes its upstream routing:
   ```bash
   docker compose restart nginx
   ```

2. Verify containers are healthy:
   ```bash
   docker compose ps
   docker compose logs nginx
   docker compose logs web
   ```

After restarting nginx, it reconnected to the updated `web` container IP and the 502 errors disappeared.
