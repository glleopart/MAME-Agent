# MAME — MAterials for ME

## Complete Development Workflow

---

## 1. SYSTEM ARCHITECTURE

```
┌──────────────────────────────────────────────────────────┐
│                  ELECTRON DESKTOP SHELL                   │
│  ┌─────────────────────┐  ┌────────────────────────────┐ │
│  │     Chat Panel       │  │   Document Viewer Panel    │ │
│  │  (React + AI SDK UI) │  │  (PDF/text select + review)│ │
│  └──────────┬──────────┘  └─────────────┬──────────────┘ │
│             │                           │                 │
│  ┌──────────▼───────────────────────────▼──────────────┐ │
│  │              MASTRA AGENT CORE (TypeScript)          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │ │
│  │  │  Agent    │  │  Memory  │  │  RAG Pipeline    │  │ │
│  │  │  (LLM +  │  │  (thread │  │  (papers index + │  │ │
│  │  │  reasoning│  │  history │  │  doc embeddings) │  │ │
│  │  │  loop)   │  │  + facts)│  │                  │  │ │
│  │  └────┬─────┘  └──────────┘  └──────────────────┘  │ │
│  │       │                                             │ │
│  │  ┌────▼──────────────────────────────────────────┐  │ │
│  │  │                  TOOL LAYER                    │  │ │
│  │  │                                                │  │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │  │ │
│  │  │  │ Tool 1:  │ │ Tool 2:  │ │  Tool 3:      │  │  │ │
│  │  │  │ Materials│ │ Script   │ │  Papers       │  │  │ │
│  │  │  │ Project  │ │ Repo     │ │  Search       │  │  │ │
│  │  │  │ API      │ │ Manager  │ │  (RAG)        │  │  │ │
│  │  │  └────┬─────┘ └────┬─────┘ └──────┬────────┘  │  │ │
│  │  │       │            │               │           │  │ │
│  │  │  ┌────┼────────────┼───────────────┼────────┐  │  │ │
│  │  │  │ Tool 4:        │  Tool 5:               │  │  │ │
│  │  │  │ Document       │  Code Execution        │  │  │ │
│  │  │  │ Interaction    │  (OpenCode bridge)     │  │  │ │
│  │  │  └────────────────┴────────────────────────┘  │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌───────────────────────────────────────────────────────┐│
│  │              EXTERNAL CONNECTIONS                      ││
│  │                                                        ││
│  │  ┌──────────┐  ┌──────────────┐  ┌────────────────┐  ││
│  │  │Materials │  │ DFT Script   │  │  Vector DB     │  ││
│  │  │Project   │  │ Repository   │  │  (papers +     │  ││
│  │  │REST API  │  │ (local git)  │  │  docs index)   │  ││
│  │  └──────────┘  └──────────────┘  └────────────────┘  ││
│  │                                                        ││
│  │  ┌──────────────┐  ┌──────────────────────────────┐   ││
│  │  │ OpenCode     │  │  Python Runtime              │   ││
│  │  │ (Go binary)  │  │  (pymatgen, mp-api, ASE)     │   ││
│  │  └──────────────┘  └──────────────────────────────┘   ││
│  └───────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

---

## 2. KEY COMPONENTS AND INTERACTIONS

### 2.1 Component Map

| Component | Technology | Role |
|-----------|-----------|------|
| **Agent Core** | Mastra (TypeScript) | Orchestrates reasoning, tool calls, memory, and RAG |
| **Code Execution** | OpenCode (Go binary) | Executes/modifies DFT scripts via terminal agent |
| **Materials Data** | Materials Project REST API + MCP | Searches materials, retrieves properties |
| **Script Repository** | Local git repo + file indexing | Stores DFT scripts, input files, workflows |
| **Papers Index** | Vector DB (LibSQL/PGVector) + embeddings | Semantic search over scientific papers |
| **Document Interaction** | PDF parser + text selection | User selects text → agent processes it |
| **Desktop UI** | Electron + React | Chat interface + document viewer + theming |
| **Python Bridge** | Child process / MCP server | Runs pymatgen, mp-api, ASE scripts |

### 2.2 How Components Interact

```
User types in chat
    │
    ▼
Electron IPC ──► Mastra Agent receives message
    │
    ▼
Agent reasons about intent (LLM call)
    │
    ├── "Search for TiO2 band gap" ──► Tool 1: Materials Project API
    │                                        │
    │                                        ▼
    │                                   Python MCP server calls mp-api
    │                                        │
    │                                        ▼
    │                                   Returns structured data to agent
    │
    ├── "Generate VASP input for this" ──► Tool 2: Script Repo Manager
    │                                        │
    │                                        ▼
    │                                   Searches repo for matching template
    │                                        │
    │                                        ▼
    │                                   Tool 5: OpenCode modifies/generates script
    │
    ├── "What papers support this?" ──► Tool 3: RAG pipeline
    │                                        │
    │                                        ▼
    │                                   Embeds query → vector search → returns chunks
    │
    ├── "Review this paragraph" ──► Tool 4: Document reader
    │                                    │
    │                                    ▼
    │                               Extracts selected text
    │                                    │
    │                                    ▼
    │                               Agent reasons + cross-refs with MP data
    │
    ▼
Agent composes response
    │
    ▼
Electron IPC ──► UI renders response in chat
```

---

## 3. DATA FLOW

### 3.1 Materials Project Query Flow

```
User question ──► Agent parses intent
    │
    ▼
Agent calls `searchMaterials` tool
    │
    ▼
Tool sends HTTP request to MP REST API
(or invokes Python MCP server with mp-api)
    │
    ▼
MP returns JSON (material_id, band_gap, structure, ...)
    │
    ▼
Agent formats response + optionally stores in memory
    │
    ▼
Response rendered in chat (with tables, property cards)
```

### 3.2 Script Generation Flow

```
User: "Generate INCAR for relaxation of mp-1234"
    │
    ▼
Agent calls `searchScriptRepo` tool
    │
    ▼
Tool scans repo index for matching templates
    │
    ▼
Returns best-match template path + metadata
    │
    ▼
Agent calls `generateScript` tool (OpenCode bridge)
    │
    ▼
OpenCode reads template, modifies parameters for mp-1234
    │
    ▼
Returns generated file content
    │
    ▼
Agent presents file in chat + option to download
```

### 3.3 RAG (Papers) Flow

```
Papers (PDFs) ──► Chunked + embedded ──► Stored in vector DB
                                              │
User question ──► Embedded ──────────────────►│
                                              ▼
                                         Cosine similarity search
                                              │
                                              ▼
                                         Top-K chunks returned
                                              │
                                              ▼
                                         Agent uses chunks as context
                                              │
                                              ▼
                                         Response with citations
```

---

## 4. AGENT DESIGN

### 4.1 Agent Configuration

```
MAME Agent
├── Model: Claude Sonnet (via Anthropic provider)
├── System prompt: Materials science specialist
│   ├── Domain knowledge context
│   ├── Multi-language instructions (ES/EN/IT)
│   └── Response format guidelines
├── Tools: [5 tools defined below]
├── Memory: Thread-based + semantic (working memory)
└── RAG: Papers pipeline connected
```

### 4.2 Tools Definition

| Tool Name | Input | Output | What it does |
|-----------|-------|--------|-------------|
| `searchMaterials` | formula, chemsys, mp-id, property filters | JSON array of materials | Queries Materials Project API |
| `getMaterialProperties` | material_id, property list | Detailed property object | Gets specific properties for one material |
| `searchScriptRepo` | task type (relaxation, DOS, etc.), code (VASP/QE), keywords | File paths + metadata | Finds matching scripts in local repo |
| `executeScript` | script path, parameters, action (run/modify/generate) | Script output or new file content | Uses OpenCode to execute or modify scripts |
| `searchPapers` | natural language query | Ranked chunks with source info | Semantic search over indexed papers |

### 4.3 Memory Strategy

```
Thread Memory (per conversation)
├── Message history (user + agent turns)
├── Working memory (key facts extracted during conversation)
│   e.g., "User is working on TiO2 anatase for photocatalysis"
└── Stored between sessions via Mastra's storage layer

Semantic Memory (cross-conversation)
├── User preferences (preferred DFT code, common systems)
└── Frequently accessed materials (cached results)
```

### 4.4 Reasoning Loop

```
1. Receive user message
2. Check memory for relevant context
3. Classify intent:
   a. Data query → Materials Project tools
   b. Script request → Script repo + OpenCode tools
   c. Literature question → RAG pipeline
   d. Document review → Document parser + cross-reference tools
   e. General question → Direct LLM response
4. Execute tool(s) — may chain multiple tools
5. Synthesize results into response
6. Update working memory with new facts
7. Return response in user's language
```

---

## 5. INTEGRATION STRATEGY

### 5.1 Materials Project Integration

**Approach**: Python MCP server wrapping `mp-api`

**Why MCP?**
- mp-api is Python-only (pymatgen dependency), Mastra is TypeScript
- MCP is natively supported by both Mastra and OpenCode
- mp-api v0.46+ already has MCP extras (`pip install mp-api[mcp]`)
- Clean separation: Python handles MP data, TypeScript handles agent logic

**Alternative considered**: Direct REST calls from TypeScript.
**Why rejected**: The MP REST API is complex (many endpoints, pagination, nested structures). mp-api handles all of this. Wrapping it in MCP gives us the best of both worlds.

### 5.2 Script Repository Integration

**Approach**: Local git repository with indexed metadata

```
dft-scripts/
├── vasp/
│   ├── relaxation/
│   │   ├── INCAR.template
│   │   ├── KPOINTS.template
│   │   └── metadata.json    ← indexed by agent
│   ├── band-structure/
│   ├── dos/
│   └── dielectric/
├── quantum-espresso/
│   ├── scf/
│   ├── bands/
│   └── phonons/
├── plotting/
│   ├── band_plot.py
│   ├── dos_plot.py
│   └── phase_diagram.py
└── index.json    ← master index for fast search
```

**Why local git?**
- Version controlled (you track changes to templates)
- Works offline
- OpenCode can read/modify files directly
- Users can clone and extend

### 5.3 Scientific Papers Integration

**Approach**: RAG pipeline using Mastra's built-in RAG primitives

**Ingestion flow**:
1. User drops PDFs into a designated folder
2. Background worker chunks PDFs (by section/paragraph)
3. Chunks embedded using an embedding model
4. Stored in vector DB (LibSQL with vector extension, or PGVector)

**Query flow**:
1. Agent embeds user query
2. Vector similarity search returns top-K chunks
3. Chunks injected as context into LLM call
4. Agent generates response with citations (paper title, page)

### 5.4 Document Interaction Integration

**Approach**: PDF.js in Electron + text selection API

1. User opens a PDF in the document viewer panel
2. User selects text (or clicks "review full document")
3. Selected text sent to agent via IPC
4. Agent can:
   - Cross-reference with Materials Project
   - Search papers for supporting evidence
   - Suggest corrections based on known data
   - Compare values with MP database

---

## 6. UI STRUCTURE

### 6.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│  [MAME Logo]  MAterials for ME       [Settings] [Theme] │
├───────────────────────┬─────────────────────────────────┤
│                       │                                  │
│    CHAT PANEL         │     DOCUMENT VIEWER PANEL        │
│                       │                                  │
│  ┌─────────────────┐  │  ┌───────────────────────────┐  │
│  │ Agent messages   │  │  │                           │  │
│  │ + user messages  │  │  │  PDF / text rendered      │  │
│  │ + property cards │  │  │  here                     │  │
│  │ + script blocks  │  │  │                           │  │
│  │                  │  │  │  [Select text] → sends    │  │
│  │                  │  │  │  to agent                 │  │
│  │                  │  │  │                           │  │
│  └─────────────────┘  │  └───────────────────────────┘  │
│                       │                                  │
│  ┌─────────────────┐  │  ┌───────────────────────────┐  │
│  │ [Type message]  │  │  │ [Open PDF] [Full Review]  │  │
│  │ [Attach file]   │  │  │ [Get Refs] [Compare MP]   │  │
│  └─────────────────┘  │  └───────────────────────────┘  │
├───────────────────────┴─────────────────────────────────┤
│  Status: Connected to MP API  │  Lang: ES  │  Model: ○  │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Theming System

- CSS variables for colors, fonts, spacing
- Light / Dark / Custom themes
- Logo + name configurable via settings file
- Stored in `~/.mame/config.json`

### 6.3 Internationalization (i18n)

- UI labels: i18next library (JSON translation files)
- Agent responses: System prompt includes language instruction
- Supported: English, Spanish, Italian
- Language detection: From user's OS locale or manual selection

---

## 7. DEVELOPMENT PHASES

---

### PHASE 0: Project Scaffolding

**Objective**: Set up the monorepo structure, tooling, and development environment.

**What to build**:
- Monorepo with `pnpm` workspaces
- Three packages: `agent/` (Mastra), `desktop/` (Electron), `scripts/` (DFT repo)
- TypeScript config, ESLint, Prettier
- `.env.example` with required API keys
- Base README.md

**Why it matters**: A clean monorepo prevents dependency chaos when Mastra (TS), Electron (TS), and Python (MCP server) coexist. Getting this right early saves hours later.

**Expected result**:
```
mame/
├── packages/
│   ├── agent/          ← Mastra agent (TypeScript)
│   ├── desktop/        ← Electron app
│   ├── mcp-server/     ← Python MCP server for MP API
│   └── scripts/        ← DFT script repository
├── pnpm-workspace.yaml
├── package.json
├── tsconfig.base.json
├── .env.example
└── README.md
```

---

### PHASE 1: Mastra Agent Core + Basic Chat

**Objective**: Get a working Mastra agent that accepts text input and returns LLM responses.

**What to build**:
- Initialize Mastra project in `packages/agent/`
- Configure LLM provider (Anthropic Claude)
- Define the MAME agent with a materials science system prompt
- Add thread-based memory (conversation persistence)
- Expose agent via local HTTP API (Mastra dev server)
- Test in Mastra Playground (built-in at localhost:4111)

**Why it matters**: This is the brain of the entire system. Every other phase plugs into this agent. If the core reasoning loop doesn't work, nothing else matters.

**Expected result**: You can open localhost:4111, type "What is the band gap of silicon?", and get a knowledgeable response from the agent using its training knowledge. No tools yet — just LLM + memory.

---

### PHASE 2: Materials Project API Integration (Tool #1)

**Objective**: Give the agent the ability to query real materials data from Materials Project.

**What to build**:
- Python MCP server in `packages/mcp-server/`
  - Uses `mp-api` (MPRester) to query Materials Project
  - Exposes tools: `search_materials`, `get_properties`, `compare_materials`
- Connect MCP server to Mastra agent
- Define Mastra tool wrappers that call the MCP tools
- Handle API key management (env variable)

**Why it matters**: This transforms the agent from a chatbot into a data-connected scientific assistant. Real-time access to 150,000+ materials with computed properties is the core value proposition.

**Expected result**: User asks "Compare the band gaps of TiO2 rutile and anatase" → agent calls MP API → returns real data with mp-ids, band gap values, and crystal system info.

---

### PHASE 3: Script Repository + Code Tools (Tool #2)

**Objective**: Let the agent find, suggest, modify, and generate DFT scripts.

**What to build**:
- Populate `packages/scripts/` with initial DFT templates
  - VASP: relaxation, band structure, DOS, dielectric
  - Quantum ESPRESSO: SCF, bands, phonons
  - Plotting: band plots, DOS plots
- Create `index.json` metadata file (task type, code, description, parameters)
- Mastra tool: `searchScriptRepo` — searches index by keywords/task type
- Mastra tool: `executeScript` — bridges to OpenCode for file modification
  - OpenCode reads the template
  - Modifies parameters based on agent instructions
  - Returns the generated file

**Why it matters**: Scientists spend enormous time writing and adapting input files. An agent that knows your script library and can customize templates per material saves hours per calculation.

**Expected result**: User asks "Generate a VASP relaxation input for mp-149 (silicon)" → agent finds relaxation template → calls MP API for structure → fills template with correct POSCAR, INCAR parameters → returns downloadable files.

---

### PHASE 4: Scientific Papers RAG (Tool #3)

**Objective**: Let the agent search and cite from a library of scientific papers.

**What to build**:
- PDF ingestion pipeline:
  - Read PDFs from a designated folder (`~/.mame/papers/`)
  - Chunk by sections/paragraphs (using Mastra's document chunking)
  - Embed chunks (using an embedding model via Mastra's RAG primitives)
  - Store in vector DB (LibSQL with vector extension — Mastra's default)
- Mastra tool: `searchPapers` — semantic search over the index
- Citation formatting: Include paper title, authors, page number in responses

**Why it matters**: Scientific reasoning requires references. An agent that can back its claims with actual papers is trustworthy. Without this, it's just an LLM guessing.

**Expected result**: User asks "What DFT functional is best for calculating TiO2 band gaps?" → agent searches papers → finds relevant chunks discussing HSE06 vs PBE+U → responds with citations.

---

### PHASE 5: Document Interaction (Tool #4)

**Objective**: Let users interact with their own documents through the agent.

**What to build**:
- PDF viewer component (using PDF.js or react-pdf)
- Text selection handler: captures selected text + page info
- IPC channel: sends selected text from Electron to Mastra agent
- Agent actions on selected text:
  - "Find references" → RAG search
  - "Check against MP data" → Materials Project lookup
  - "Correct this" → Agent reasons about accuracy
  - "Full document review" → Summarize + flag potential issues
- Mastra tool: `processDocumentSelection` — receives text + action type

**Why it matters**: Researchers constantly read papers and want to validate claims, find related work, or compare reported values with databases. This makes the agent a reading companion.

**Expected result**: User opens a PDF, selects a paragraph claiming "TiO2 has a band gap of 3.0 eV", clicks "Compare with MP" → agent queries MP → responds "Materials Project reports 3.03 eV for rutile (mp-2657) and 3.23 eV for anatase (mp-390). The claim is consistent with rutile."

---

### PHASE 6: Multi-Language Support

**Objective**: Make both the UI and agent responses work in English, Spanish, and Italian.

**What to build**:
- i18next setup in Electron app
- Translation files: `en.json`, `es.json`, `it.json` for all UI strings
- System prompt modification: Include language instruction
  - "Respond in the same language the user writes in"
  - Or respect the user's explicit language preference
- Language selector in settings panel
- Test agent responses in all three languages

**Why it matters**: MAME targets an international research community. Spanish and Italian are your primary user languages. A tool that only works in English loses half its audience.

**Expected result**: User writes "¿Cuál es el gap de banda del silicio?" → agent responds in Spanish with real data from MP.

---

### PHASE 7: Desktop UI with Electron

**Objective**: Package everything into a desktop application with a polished interface.

**What to build**:
- Electron app in `packages/desktop/`
- React frontend with two-panel layout (chat + document viewer)
- IPC bridge: Electron main process ↔ Mastra agent server
- Theming system (CSS variables, light/dark mode)
- Settings panel (API keys, language, theme, model selection)
- Custom branding: MAME logo + name in title bar
- File handling: drag-and-drop PDFs, script downloads
- Agent connection management: startup checks for MP API, MCP server

**Why it matters**: A desktop app is the delivery vehicle. Without it, MAME is just a developer tool. The UI makes it accessible to every researcher, not just programmers.

**Expected result**: A standalone window with a chat panel on the left, document viewer on the right, MAME branding, and full functionality from Phases 1-6.

---

### PHASE 8: Packaging and Distribution

**Objective**: Make MAME installable by other users on Windows, macOS, and Linux.

**What to build**:
- Electron Builder or Electron Forge configuration
- Platform-specific installers:
  - `.dmg` for macOS
  - `.exe` / `.msi` for Windows
  - `.AppImage` / `.deb` for Linux
- Auto-updater (electron-updater)
- First-run setup wizard:
  - Enter Materials Project API key
  - Choose LLM provider + API key
  - Select language
  - Point to papers folder (optional)
- Bundle Python runtime + MCP server (using PyInstaller or embedded Python)
- GitHub Releases for distribution
- README with installation instructions + screenshots

**Why it matters**: The goal is "other users can install and use" — not just you running it locally. Packaging is the difference between a project and a product.

**Expected result**: A user downloads MAME from GitHub, runs the installer, enters their API keys, and starts chatting with a materials science AI assistant.

---

## 8. PHASE DEPENDENCY MAP

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3
                │                       │
                │            ┌──────────┘
                │            ▼
                ├──► Phase 4 (can start after Phase 1)
                │
                ├──► Phase 6 (can start after Phase 1)
                │
                └──► Phase 5 (needs Phase 2 + Phase 4)
                         │
                         ▼
                     Phase 7 (needs Phase 1-6)
                         │
                         ▼
                     Phase 8 (needs Phase 7)
```

**Parallel work possible**:
- Phase 4 (RAG) can start after Phase 1
- Phase 6 (i18n) can start after Phase 1
- Phase 3 (scripts) can start once Phase 2 is working

---

## 9. TECHNOLOGY DECISIONS SUMMARY

| Decision | Choice | Why |
|----------|--------|-----|
| Agent framework | Mastra | TypeScript, built-in tools/memory/RAG, MCP support, active community (7.5K+ stars) |
| Code execution | OpenCode | Go binary, terminal-native, file read/write/execute, MCP compatible |
| MP API bridge | Python MCP server | mp-api is Python-only; MCP provides clean cross-language bridge |
| Vector DB | LibSQL (Turso) | Mastra's default, embedded (no external server), supports vector extension |
| Desktop shell | Electron | Cross-platform, React-compatible, mature ecosystem, PDF.js integration |
| Frontend | React + Tailwind | Mastra team recommends React; Tailwind for fast theming |
| Packaging | Electron Forge | Handles cross-platform builds, code signing, auto-update |
| i18n | i18next | Most used i18n library for React, JSON-based translations |
| Python bundling | Embedded Python (python-build-standalone) | No system Python dependency for end users |

---

## 10. RISK MAP

| Risk | Impact | Mitigation |
|------|--------|-----------|
| MP API rate limits | Medium | Cache results locally; batch queries; respect API guidelines |
| Python+TypeScript bridge complexity | High | MCP standardizes the interface; test MCP server independently |
| Electron app size (bundling Python) | Medium | Use python-build-standalone (~30MB); strip unused packages |
| RAG quality for scientific papers | High | Tune chunk size; use section-aware chunking; test with real papers |
| OpenCode integration stability | Medium | Abstract behind a clean interface; fallback to direct subprocess |
| Multi-language LLM responses | Low | System prompt engineering; test extensively in all 3 languages |
| Cross-platform packaging | Medium | Test on all 3 OS early; CI with GitHub Actions |

---

## WHAT HAPPENS NEXT

I stop here. You tell me which phase to start with, and I will guide you through it step by step — with architecture decisions, file-by-file implementation, and testing at each stage.

Recommended starting order: **Phase 0 → Phase 1 → Phase 2** (this gives you a working agent with real data in ~3 sessions).
