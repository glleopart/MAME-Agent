# MAME — MAterials for ME

AI-powered desktop agent for computational materials science.

## Stack
- Mastra v1 (TypeScript agent framework)
- OpenCode GO / Kimi K2.5 (LLM provider)
- LibSQL for storage/memory
- Python MCP server for Materials Project API, web search, and script library (Phase 3 — implemented)
- Electron + React (desktop, Phase 7)

## Structure
- packages/agent/ — Mastra agent (main codebase)
- packages/desktop/ — Electron app (Phase 7)
- packages/mcp-server/ — Python MCP server (FastMCP + mp-api + duckduckgo-search + httpx)
- packages/scripts/ — DFT input template library (FHI-aims and QE)

## Key files
- packages/agent/src/mastra/index.ts — Mastra entry point
- packages/agent/src/mastra/agents/mame-agent.ts — Agent definition (uses MCP tools)
- packages/agent/src/mastra/memory.ts — LibSQL persistent memory
- packages/agent/src/mastra/mcp.ts — MCPClient wired to Python MCP server
- packages/agent/.env — API keys (OPENCODE_API_KEY, MP_API_KEY)
- packages/mcp-server/src/mame_mcp/server.py — All MCP tools (8 total)
- packages/scripts/index.json — Script library index

## MCP tools (8 total)
- search_materials — search Materials Project by formula
- get_electronic_properties — band gap, VBM, CBM, magnetic ordering
- get_structure — crystal structure (JSON or CIF)
- get_dos — density of states
- web_search — DuckDuckGo search for GGA+U values, methodology, papers
- fetch_documentation — fetch and read any documentation/manual page URL
- list_scripts — list local DFT input templates (filter by code or task)
- get_script — return template file contents by ID

## Script library (packages/scripts/)
Ready templates: aims-scf, aims-relax, aims-bands, aims-dos,
qe-scf, qe-nscf, qe-relax, qe-vc-relax, qe-dos
All templates include inline comments and pre-commented GGA+U options.

## Commands
- pnpm dev:agent — starts Mastra dev server at localhost:4111
- mastra dev runs from packages/agent/

## Path resolution rule
All file paths use import.meta.url (not process.cwd()) because mastra dev
runs bundled code from packages/agent/.mastra/output/. Both src/mastra/ and
.mastra/output/ are 2 levels below packages/agent/, so relative paths work
identically in both contexts.

## MCP server setup
After adding new Python dependencies, reinstall before starting the agent:
```
cd packages/mcp-server
uv sync   # or: uv sync --no-binary :all:  (on WSL1 with low memory)
```
MP_API_KEY must be set in packages/agent/.env — it is passed to the Python
process by the MCPClient in mcp.ts.

## WSL1 SQLite WAL issue (known)
In WSL1, LibSQLStore sets PRAGMA journal_mode=WAL which creates mame.db-shm and
mame.db-wal files. After an unclean shutdown, stale WAL files cause
SQLITE_PROTOCOL: locking protocol on the /api/memory/threads endpoint, which
makes the Mastra playground show a blank chatbox (chat interface fails to load).

Fix: delete the stale files before starting the server:
  rm packages/agent/data/mame.db-shm packages/agent/data/mame.db-wal

## Next session: end-to-end tests (still pending)
Wait ~20 seconds for full startup (Python/MCP server cold start on WSL1).
1. uv run mame-mcp  (in packages/mcp-server) — should hang on stdin, no errors
2. pnpm dev:agent   — should reach "ready" at localhost:4111
3. In the Mastra playground ask: "What is the band gap of TiO2?"
   Expected: agent calls search_materials then get_electronic_properties
4. Ask: "Give me an FHI-aims SCF input for Fe2O3 with GGA+U"
   Expected: agent calls get_script("aims-scf") and web_search for U values

## Remote
https://github.com/glleopart/MAME-Agent (public)
