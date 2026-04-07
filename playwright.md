docker run -d -i --rm --init --pull=always \
  --entrypoint node \
  --name playwright \
  -p 8931:8931 \
  mcr.microsoft.com/playwright/mcp \
  /app/cli.js --headless --browser chromium --no-sandbox --port 8931 --host 0.0.0.0 --allowed-hosts '*'



codex mcp add playwright --url http://localhost:8931/mcp



{
  "mcpServers": {
    "playwright-mcp": {
      "url": "http://localhost:8931",
      "type": "streamableHttp",
      "disabled": false,
      "autoApprove": []
    }
  }
}


