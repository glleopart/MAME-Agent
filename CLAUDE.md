# MAME — MAterials for ME

AI-powered desktop agent for computational materials science.

## Stack
- Mastra v1 (TypeScript agent framework)
- OpenCode GO / Kimi K2.5 (LLM provider)
- LibSQL for storage/memory
- Python MCP server for Materials Project API (Phase 2 — implemented)
- Electron + React (desktop, Phase 7)

## Structure
- packages/agent/ — Mastra agent (main codebase)
- packages/desktop/ — Electron app (Phase 7)
- packages/mcp-server/ — Python MCP server (FastMCP + mp-api)
- packages/scripts/ — DFT script repository

## Key files
- packages/agent/src/mastra/index.ts — Mastra entry point
- packages/agent/src/mastra/agents/mame-agent.ts — Agent definition (uses MCP tools)
- packages/agent/src/mastra/memory.ts — LibSQL persistent memory
- packages/agent/src/mastra/mcp.ts — MCPClient wired to Python MCP server
- packages/agent/.env — API keys (OPENCODE_API_KEY, MP_API_KEY)
- packages/mcp-server/src/mame_mcp/server.py — MCP tools (search_materials, get_electronic_properties, get_structure, get_dos)

## Commands
- pnpm dev:agent — starts Mastra dev server at localhost:4111
- mastra dev runs from packages/agent/

## Path resolution rule
All file paths use import.meta.url (not process.cwd()) because mastra dev
runs bundled code from packages/agent/.mastra/output/. Both src/mastra/ and
.mastra/output/ are 2 levels below packages/agent/, so relative paths work
identically in both contexts.

## MCP server setup
The Python MCP server must be installed before starting the agent:
```
cd packages/mcp-server
uv sync   # or: uv sync --no-binary :all:  (on WSL1 with low memory)
```
MP_API_KEY must be set in packages/agent/.env — it is passed to the Python
process by the MCPClient in mcp.ts.

## Next session: end-to-end tests
1. uv run mame-mcp  (in packages/mcp-server) — should hang on stdin, no errors
2. pnpm dev:agent   — should reach "ready" at localhost:4111
3. In the Mastra playground ask: "What is the band gap of TiO2?"
   Expected: agent calls search_materials then get_electronic_properties

## Remote
https://github.com/glleopart/MAME-Agent (public)
