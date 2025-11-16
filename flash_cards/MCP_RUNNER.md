## Automating flash cards

Choose the workflow that fits your tooling:

- **OpenAI Custom GPT** – simplest path if you mainly use ChatGPT. Import the
  provided OpenAPI file and you are done.
- **MCP runner** – needed when you want to expose the API to MCP-aware clients
  such as Claude Desktop or Cursor. Keep reading after the OpenAI section.

---

### Option A – OpenAI Custom GPT / Actions

1. **Generate & store the shared token** (used by both approaches). If you
   haven’t already, create a strong value and add it to `.env`:

   ```bash
   python - <<'PY'
   import secrets; print(secrets.token_urlsafe(32))
   PY
   ```

   ```
   FLASH_CARDS_MCP_TOKEN=your-generated-token
   ```

   Redeploy with `./deploy.sh` so the environment variable is loaded.

2. **Download the OpenAPI file** located at
   `flash_cards/openapi_flash_cards.yaml`. The schema uses OpenAPI 3.1.0 (the
   version required by the GPT builder), so you can upload it directly when the
   UI asks for an “Action schema.”

3. **Create or edit your GPT** on https://chatgpt.com:
   - Go to *Explore GPTs → Create*.
   - In the *Actions* tab, click *Create new action* and choose *Import from file*.
   - Select `openapi_flash_cards.yaml`.
   - When the builder asks for credentials, define a secret named
     `X-MCP-TOKEN` (or any key) containing the same token you put in `.env`.

4. Publish/save the GPT. ChatGPT will now call
   `https://bricolle-family.fr/flash_cards/api/questions/` and `/categories/`
   directly whenever you invoke the action.

You can reuse the same OpenAPI file for any other tool that accepts OpenAPI
schemas (Zapier actions, LangGraph, etc.).

---

### Option B – MCP runner setup

These steps spin up a Model Context Protocol runner that exposes `create_question`
and `list_categories` from `flash_cards/mcp_server.json` so any MCP‑aware client
(Claude Desktop, Cursor, etc.) can call them.

#### 1. Configure authentication

1. Pick a strong shared token and store it in `.env` so the Django API accepts
   machine traffic without a login session:

   ```bash
   python - <<'PY' | tr -d '\n'
   import secrets; print(secrets.token_urlsafe(32))
   PY
   ```

2. Add the value to `.env` and redeploy (`./deploy.sh` will rebuild everything):

   ```
   FLASH_CARDS_MCP_TOKEN=your-generated-token
   ```

   The `flash_cards` API now accepts authenticated calls that include the header
   `X-MCP-TOKEN: your-generated-token`.

#### 2. Install the HTTP MCP runner on the server

Any machine that can reach your Django instance may host the runner; using the
same cloud VM keeps things simple. Install Node.js once (skip if it is already
available) and add the official HTTP runner:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g @modelcontextprotocol/server-http
```

> The commands above require root privileges; adapt them if you manage packages
> differently on your distro.

#### 3. Run the MCP runner

Point the runner at the JSON description and forward the MCP token as an HTTP
header for every upstream call:

```bash
export FLASH_CARDS_MCP_TOKEN=your-generated-token
mcp-server-http \
  --config /home/louis/Custom_projects/bricolle-family/flash_cards/mcp_server.json \
  --port 7410 \
  --header "X-MCP-TOKEN: ${FLASH_CARDS_MCP_TOKEN}"
```

Keep the process alive in a service manager (systemd, pm2, Supervisor) or run it
inside tmux/screen. Expose or tunnel `7410` so your MCP client can connect.

#### 4. Example Claude Desktop entry

Add this block to `~/Library/Application Support/Claude/claude_desktop_config.json`
(or the equivalent on Linux/Windows) so Claude Desktop loads the runner:

```json
"mcpServers": {
  "flashCards": {
    "command": "ssh",
    "args": [
      "louis@your-server",
      "mcp-server-http",
      "--config",
      "/home/louis/Custom_projects/bricolle-family/flash_cards/mcp_server.json",
      "--port",
      "7410",
      "--header",
      "X-MCP-TOKEN:your-generated-token"
    ],
    "disabled": false
  }
}
```

Replace the SSH target or process launcher with whatever is convenient: you can
call `mcp-server-http` locally if the Django app is reachable from your laptop.

#### 5. Health check

Before wiring a real tool, confirm the runner can invoke your API:

```bash
curl -H "X-MCP-TOKEN: ${FLASH_CARDS_MCP_TOKEN}" \
  https://bricolle-family.fr/flash_cards/api/categories/
```

If the JSON response contains the categories list, the MCP runner can forward
the same call successfully.

That’s it—deploy the Django app as usual with `./deploy.sh`, keep the MCP runner
online, and register it as a tool source inside your preferred MCP client.
