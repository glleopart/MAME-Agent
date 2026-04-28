# MAME — MAterials for ME

AI-powered desktop agent for computational materials science. MAME combines a
Mastra-based conversational agent with the Materials Project database, web
search, and a curated library of DFT input templates for FHI-aims and Quantum
ESPRESSO.

---

## Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | ≥ 22.13 | Agent runtime |
| pnpm | ≥ 9.0 | JS package manager |
| Python | ≥ 3.11 | MCP server |
| uv | any | Python package manager |

---

## First-time setup

### 1. Clone and install JS dependencies

```bash
git clone https://github.com/glleopart/MAME-Agent.git
cd MAME-Agent
pnpm install
```

### 2. Install the Python MCP server

```bash
cd packages/mcp-server
uv sync
# On WSL1 or low-memory systems use:
# uv sync --no-binary :all:
cd ../..
```

### 3. Configure API keys

Create `packages/agent/.env` with your keys:

```env
OPENCODE_API_KEY=your_opencode_go_key
MP_API_KEY=your_materials_project_key
```

- **OPENCODE_API_KEY** — from [opencode.ai](https://opencode.ai) (Kimi K2.5 model)
- **MP_API_KEY** — from [materialsproject.org/api](https://next-gen.materialsproject.org/api)

---

## Running the agent

The MCP server is launched automatically by the agent. You only need one command:

```bash
pnpm dev:agent
```

This starts the Mastra dev server at **http://localhost:4111**.

Open the Mastra playground in your browser and start asking questions, for example:

- *"What is the band gap of TiO2?"*
- *"Give me an FHI-aims SCF input file for Fe2O3 with GGA+U"*
- *"What Hubbard U value should I use for NiO?"*

### Verify the MCP server starts cleanly (optional)

To test the Python server in isolation before running the agent:

```bash
cd packages/mcp-server
uv run mame-mcp
# Should hang waiting on stdin — no errors means it is working.
# Press Ctrl+C to exit.
```

---

## Updating dependencies

### JS dependencies (agent)

```bash
# Update all packages to latest compatible versions
pnpm update -r

# Or update a specific package
pnpm --filter @mame/agent update @mastra/core
```

After updating, restart the agent with `pnpm dev:agent`.

### Python dependencies (MCP server)

```bash
cd packages/mcp-server

# Upgrade all packages to latest versions allowed by pyproject.toml
uv sync --upgrade

# Upgrade a specific package
uv sync --upgrade-package duckduckgo-search

# After adding a new dependency to pyproject.toml
uv sync
```

### Adding a new Python dependency

1. Add it to the `dependencies` list in `packages/mcp-server/pyproject.toml`
2. Run `uv sync` in `packages/mcp-server/`
3. Restart the agent

---

## Reinstalling from scratch

Use this if dependencies become corrupted or after a major version change.

### Full reinstall (JS + Python)

```bash
# Remove all JS artifacts
pnpm clean          # removes node_modules, dist, .build in all packages
pnpm install        # reinstall everything

# Reinstall Python environment
cd packages/mcp-server
rm -rf .venv
uv sync             # (or uv sync --no-binary :all: on WSL1)
cd ../..
```

### Reinstall JS only

```bash
rm -rf node_modules packages/agent/node_modules
pnpm install
```

### Reinstall Python only

```bash
cd packages/mcp-server
rm -rf .venv
uv sync
```

---

## Project structure

```
MAME-Agent/
├── packages/
│   ├── agent/                  # Mastra agent (TypeScript)
│   │   ├── src/mastra/
│   │   │   ├── index.ts        # Mastra entry point
│   │   │   ├── agents/
│   │   │   │   └── mame-agent.ts
│   │   │   ├── memory.ts       # LibSQL persistent memory
│   │   │   └── mcp.ts          # MCP client → Python server
│   │   └── .env                # API keys (not committed)
│   ├── mcp-server/             # Python MCP server (FastMCP)
│   │   ├── src/mame_mcp/
│   │   │   └── server.py       # All MCP tools
│   │   └── pyproject.toml
│   ├── scripts/                # DFT input template library
│   │   ├── index.json          # Template index
│   │   ├── Fhi-aims/           # FHI-aims templates (scf, relax, bands, dos)
│   │   └── QE/                 # Quantum ESPRESSO templates (scf, nscf, relax, vc-relax, dos)
│   └── desktop/                # Electron app (Phase 7 — not yet implemented)
└── package.json                # Monorepo scripts
```

---

## Available MCP tools

| Tool | Description |
|------|-------------|
| `search_materials` | Search Materials Project by formula |
| `get_electronic_properties` | Band gap, VBM, CBM, magnetic ordering |
| `get_structure` | Crystal structure (JSON or CIF) |
| `get_dos` | Density of states data |
| `web_search` | Search the web for GGA+U values, methodology, papers |
| `fetch_documentation` | Fetch and read any documentation or manual page |
| `list_scripts` | List local DFT input templates (filterable by code/task) |
| `get_script` | Return template file contents by ID |

---

## Troubleshooting

**Agent fails to start / MCP tools not found**
- Check that `packages/agent/.env` exists and has both API keys.
- Run `uv run mame-mcp` in `packages/mcp-server/` and look for import errors.
- Reinstall the Python environment: `rm -rf .venv && uv sync`.

**`uv sync` fails on WSL1**
- Use `uv sync --no-binary :all:` to build packages from source.

**`pnpm dev:agent` reports port already in use**
- Kill the existing process: `kill $(lsof -t -i:4111)` or restart the terminal.

**LibSQL / database errors**
- The database lives at `packages/agent/data/mame.db` (gitignored).
- To reset memory: `rm packages/agent/data/mame.db` and restart the agent.
