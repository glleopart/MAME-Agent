# MAME — MAterials for ME

AI-powered desktop agent for computational materials science.

## Stack
- Mastra v1 (TypeScript agent framework)
- OpenCode GO / Kimi K2.5 (LLM provider)
- LibSQL for storage/memory
- Electron + React (desktop, coming later)
- Python MCP server for Materials Project API (coming later)

## Structure
- packages/agent/ — Mastra agent (main codebase)
- packages/desktop/ — Electron app (Phase 7)
- packages/mcp-server/ — Python MCP server (Phase 2)
- packages/scripts/ — DFT script repository

## Key files
- packages/agent/src/mastra/index.ts — Mastra entry point
- packages/agent/src/mastra/agents/mame-agent.ts — Agent definition
- packages/agent/.env — API keys (OPENCODE_API_KEY)

## Commands
- pnpm dev:agent — starts Mastra dev server at localhost:4111
- mastra dev runs from packages/agent/

## Current issue
LibSQLStore path resolution — relative paths fail because mastra dev
runs bundled code from packages/agent/.mastra/output/. Use absolute
paths with process.cwd().
