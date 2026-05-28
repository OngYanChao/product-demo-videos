# V0 Install Research — Four Clients

*Research for Video 0 (Installing the Parallax MCP). Built by reading the Parallax plugin config directly and then checking the official install docs for each target client.*

*April 2026.*

---

## What Parallax actually needs to connect

Pulled straight from the plugin files on disk (`plugin_015A5ZUDZcthymkzdmBgQkgY`):

**`.claude-plugin/plugin.json`** declares a `user_config` named `PARALLAX_API_KEY` (type `secret`).

**`.mcp.json`** is a single HTTP MCP server:

```json
{
  "mcpServers": {
    "parallax": {
      "type": "http",
      "url": "https://mcp.chicago.global/api/mcp",
      "headers": {
        "Authorization": "Bearer ${PARALLAX_API_KEY}"
      }
    }
  }
}
```

So the connection profile every client has to reproduce is:

- **Transport:** streamable HTTP (not stdio, not SSE)
- **URL:** `https://mcp.chicago.global/api/mcp`
- **Auth:** static `Authorization: Bearer <api_key>` header
- **No OAuth.** Key is provisioned by Chicago Global and pasted once.

That's the technical surface. Everything below is "how does each client let me plug those three facts in, and what breaks."

---

## The one distinction that changes the whole video

**Only Claude Code consumes the full Parallax plugin.** The plugin package is the 10 slash commands (`/parallax:stock`, `/parallax:deep-dive`, etc.) + 7 skills + the `.mcp.json`. That whole bundle only works as a Claude Code plugin.

The other three clients (Claude Desktop, Codex CLI, Qwen CLI) can only consume the raw MCP server. They get the underlying tools (`search_stocks`, `analyze_portfolio`, `macro_analyst`, etc.) but **no `/parallax:` slash commands and no embedded skill guidance.** Users invoke capabilities by natural language: *"Run a Parallax deep dive on NVDA"* instead of `/parallax:deep-dive NVDA`.

This matters for V0 and V0.5. The current beat sheets assume `/parallax:stock AAPL` works as a sanity check in all four clients. It doesn't. Rewrite the sanity-check as an NL prompt ("Give me a Parallax stock brief for AAPL") so it's genuinely identical across clients. V0.5's quad-split payoff is actually stronger if it uses NL — it proves the MCP-native claim more honestly.

---

## Client 1 — Claude Desktop

**Verdict: this is the weakest of the four install flows and needs special handling in V0.**

### Why the GUI path doesn't work

Claude Desktop exposes a "Custom connectors" UI (Settings → Connectors → Add → Custom → Web). It accepts a remote MCP URL and, under Advanced settings, an OAuth Client ID and Client Secret.

**It does not support static bearer tokens or custom headers.** This is a known, open product gap — Anthropic issue #112, still labelled `bug`, `server-developer-report` as of late March 2026. Any MCP server that authenticates with a static `Authorization: Bearer` header (like Parallax) cannot be added through the GUI.

There's also a network wrinkle: the GUI custom-connector path brokers traffic through Anthropic's cloud, not the user's local machine. If Parallax ever gates on client IPs, this matters. Today it's fine (MCP is on a public domain) but worth flagging to the Chicago Global infra team before recording.

### The workaround: local config file + `mcp-remote` shim

Users edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows) and add:

```json
{
  "mcpServers": {
    "parallax": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://mcp.chicago.global/api/mcp",
        "--header",
        "Authorization: Bearer ${PARALLAX_API_KEY}"
      ],
      "env": {
        "PARALLAX_API_KEY": "pk_live_..."
      }
    }
  }
}
```

Then restart Claude Desktop. `mcp-remote` (an npm shim) is what bridges stdio ↔ remote HTTP with custom headers; Claude Desktop can't speak streamable HTTP with bearer natively from config yet.

### What to do in V0

- Don't pretend there's a clean "paste URL, click Connect" flow — there isn't.
- Either (a) show the JSON file edit + restart on screen, framed as "one-time setup, copy-paste from the install doc," or (b) cut Claude Desktop from V0 entirely and only show it in V0.5 after the install story has been told in a cleaner client.
- Must-verify before filming: does Parallax plan to add OAuth? If yes by recording date, the GUI path unblocks and V0 becomes much cleaner on Claude Desktop. Worth a direct ask to engineering.

---

## Client 2 — Claude Code

**Verdict: cleanest of the four. This is the install story the video should anchor to.**

### Plugin path (recommended for the video)

If Parallax is published to a Claude Code marketplace (or installed from a local `.plugin` bundle), users run:

```
/plugin install parallax@chicago-global
```

The plugin system auto-loads `.mcp.json`, registers the 10 slash commands, registers the skills, and prompts for `PARALLAX_API_KEY` via the `user_config` declaration in `plugin.json`. This is the native path and the only way to get the `/parallax:*` slash commands.

### Raw MCP path (fallback)

If the plugin isn't in a marketplace yet, users add just the MCP server:

```
claude mcp add --transport http parallax https://mcp.chicago.global/api/mcp \
  --header "Authorization: Bearer $PARALLAX_API_KEY"
```

Or `claude mcp add-json` with the raw `.mcp.json` shape. This gives them the underlying MCP tools but none of the slash commands or skill guidance — so prefer the plugin path for the demo.

### What to do in V0

- Record the plugin-install path. It's a one-line install + API key prompt + working `/parallax:stock AAPL` verification. That's the story.
- Must-verify: is Parallax actually live on a marketplace or shipped as a local `.plugin`? Plan mentions the plugin but doesn't say where it's distributed from.

---

## Client 3 — Codex CLI (OpenAI)

**Verdict: clean CLI install. Works. But verify the Codex version covers streamable HTTP before filming.**

### What Codex CLI supports

OpenAI's docs explicitly list streamable HTTP MCP servers with bearer token auth as supported. The `codex mcp` CLI and `~/.codex/config.toml` both accept HTTP + bearer configuration:

**CLI form:**

```
codex mcp add parallax \
  --url https://mcp.chicago.global/api/mcp \
  --bearer-token-env-var PARALLAX_API_KEY
```

**Config file form (`~/.codex/config.toml`):**

```toml
[mcp_servers.parallax]
url = "https://mcp.chicago.global/api/mcp"
bearer_token_env_var = "PARALLAX_API_KEY"
```

User then exports `PARALLAX_API_KEY` in their shell (or adds it to a `.env`/shell rc file). `codex` then picks up MCP tools at startup; `/mcp` inside the TUI lists active servers.

### What to do in V0

- Show the one-line `codex mcp add --url ... --bearer-token-env-var ...` command.
- Verify Codex CLI version ≥ the release that introduced the RMCP client / streamable HTTP direct support. Older Codex builds only supported stdio launchers; a user on an old version will hit "unsupported transport" errors.
- No slash commands. Sanity check is an NL prompt.

---

## Client 4 — Qwen CLI / Qwen Code

**Verdict: supported, with a couple of quirks in property naming.**

### What Qwen Code supports

The `qwen mcp add` CLI handles streamable HTTP with auth headers:

```
qwen mcp add --transport http parallax https://mcp.chicago.global/api/mcp \
  --header "Authorization: Bearer $PARALLAX_API_KEY"
```

In `~/.qwen/settings.json` the manual form uses `httpUrl` (not `url`, which is reserved for SSE):

```json
{
  "mcpServers": {
    "parallax": {
      "httpUrl": "https://mcp.chicago.global/api/mcp",
      "headers": {
        "Authorization": "Bearer $PARALLAX_API_KEY"
      },
      "timeout": 30000
    }
  }
}
```

Env var interpolation works with `$VAR` or `${VAR}`. The `/mcp` TUI command shows connection state and discovered tools; `qwen mcp manage` opens an interactive dialog.

### Gotchas worth knowing

- **`url` vs `httpUrl`:** easy to get wrong when copying from the Claude Code `.mcp.json` (which uses `url`). Qwen treats `url` as SSE and will fail the handshake. Video must show `httpUrl`.
- **Tool name sanitization:** Qwen rewrites invalid characters in tool names to underscores and truncates names longer than 63 chars. Unlikely to affect Parallax (tool names are clean) but good to mention if a tool doesn't appear under the expected name.
- **Confirmation prompts:** Qwen prompts for approval on every tool call unless `trust: true` is set per-server. For demo fluency, set `trust: true` in the recording config.

### What to do in V0

- Show the CLI add command, not the JSON file edit.
- Have `trust: true` already set in the demo config so the video doesn't spend 30 seconds clicking "Allow" for each tool call during the sanity check.

---

## Cross-cutting implications for V0 and V0.5

Rewrite these parts of the master plan before filming:

1. **Drop "five minutes, same three steps in each client."** The install surface differs substantially: plugin manager (Claude Code), JSON file edit via `mcp-remote` (Claude Desktop), one-line CLI (Codex, Qwen). Honest framing: *"Install looks a little different in each client — we'll show all four, none take more than a minute once you have your API key."*

2. **Replace the `/parallax:stock AAPL` sanity check with a natural-language prompt.** Only Claude Code has the slash command. V0.5's quad-split should type the same NL prompt — e.g. *"Run a deep dive on NVDA using Parallax"* — into all four. That's a truer demonstration of MCP portability than showing four slash commands that only one client actually supports.

3. **Resolve the Codex support question decisively.** Plan already flags this as must-verify. Confirmed supported in current Codex CLI docs. Pin the minimum Codex version in the recording notes so any version guard added in post ("requires Codex CLI 0.x+") isn't guessed.

4. **Claude Desktop path is the most fragile.** Options in preference order:
   1. Wait until Parallax adds OAuth support, then use the GUI custom-connector path (clean demo, no JSON editing).
   2. Show the `mcp-remote` JSON workaround on screen (works today, uglier).
   3. Cut Claude Desktop from V0 and lead V0.5 with it instead, after the user has seen the concept land in a cleaner client.

5. **Pricing + speed claim ("No terminal. No IT ticket. No 12-month rollout.")** still holds as a category comparison to Bloomberg — but the JSON-editing reality on Claude Desktop undercuts "five minutes" a bit. Either soften to "Ten minutes, any client" or anchor the timer on whichever client is being shown at that moment.

---

## Things to ask engineering before V0 records

Each of these is a question for the Parallax engineering team. The answers change what gets shown on screen.

- [ ] **"Which version of Codex CLI do people need to be on?"** Older versions of Codex CLI can't connect to Parallax at all. We need to know the minimum version so the video can say "make sure you're on Codex v0.X or later" — otherwise viewers on an old version will follow the steps and hit an error.
- [ ] **"How do people actually install the Parallax plugin into Claude Code?"** Two possibilities. (a) It's published somewhere public and users install with one command — cleanest demo. (b) Users download a file from Chicago Global and install it manually. The video has to show whichever is real.
- [ ] **"Are you planning to add a 'Sign in with Parallax' login option?"** Today Parallax uses an API key (a long string of characters you paste in). Claude Desktop's setup screen can't accept API keys — only proper logins. If engineering is adding a login flow soon, Claude Desktop becomes a clean one-click demo. If not, we have to show users editing a config file, which is uglier on video.
- [ ] **"Can you give us the exact text users should paste into Claude Desktop's config file?"** Engineering should write and bless the copy-paste block so we're not inventing it. Also: pin a specific version of the `mcp-remote` helper (rather than "latest") so the video still works six months from now if `mcp-remote` changes.
- [ ] **"Does Parallax's server block any IP addresses?"** Claude Desktop's remote-connector feature routes traffic through Anthropic's servers (not the user's computer). If Parallax's firewall is locked down to specific IPs, Anthropic's IPs need to be allowed. Probably not an issue (the server is on a public address), but worth a one-line confirmation.
- [ ] **"Can we set up the Qwen demo so it doesn't ask for permission on every tool call?"** By default Qwen pops up an "Allow this tool?" dialog for every single MCP tool call. In a demo video that'd be 30 seconds of clicking Allow. There's a setting that auto-approves a trusted server — confirm it's OK to turn that on for the recording.

---

## Sources

- [Model Context Protocol — Codex | OpenAI Developers](https://developers.openai.com/codex/mcp)
- [Connect Claude Code to tools via MCP — Claude Code Docs](https://code.claude.com/docs/en/mcp)
- [MCP servers with Qwen Code — Qwen Code Docs](https://qwenlm.github.io/qwen-code-docs/en/developers/tools/mcp-server/)
- [Get started with custom connectors using remote MCP — Claude Help Center](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [Getting Started with Local MCP Servers on Claude Desktop — Claude Help Center](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Cannot configure Authorization: Bearer for custom remote MCP — anthropics/claude-ai-mcp#112](https://github.com/anthropics/claude-ai-mcp/issues/112)
