"""MAME MCP Server — Materials Project data, web search, and local script library."""

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mp_api.client import MPRester
from dotenv import load_dotenv

load_dotenv()

MP_API_KEY = os.getenv("MP_API_KEY")

# Path to packages/scripts/ — works both from src/ and from .mastra/output/
_SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "scripts"

mcp = FastMCP("mame-mcp")


# ── Materials Project tools ──────────────────────────────────────────────────

@mcp.tool()
def search_materials(formula: str, num_results: int = 10) -> list[dict]:
    """Search the Materials Project database by chemical formula or elements.

    Args:
        formula: Chemical formula (e.g. "Fe2O3", "TiO2", "GaAs")
        num_results: Maximum number of results to return (default 10)
    """
    with MPRester(MP_API_KEY) as mpr:
        results = mpr.materials.summary.search(
            formula=formula,
            fields=[
                "material_id",
                "formula_pretty",
                "band_gap",
                "is_stable",
                "energy_above_hull",
                "crystal_system",
                "space_group",
                "nsites",
            ],
        )
        return [r.model_dump(mode="json") for r in results[:num_results]]


@mcp.tool()
def get_electronic_properties(material_id: str) -> dict:
    """Get electronic properties for a material from the Materials Project.

    Args:
        material_id: Materials Project ID (e.g. "mp-1234")
    """
    with MPRester(MP_API_KEY) as mpr:
        result = mpr.materials.summary.get_data_by_id(
            material_id,
            fields=[
                "material_id",
                "formula_pretty",
                "band_gap",
                "is_gap_direct",
                "is_metal",
                "cbm",
                "vbm",
                "efermi",
                "total_magnetization",
                "ordering",
            ],
        )
        return result.model_dump(mode="json")


@mcp.tool()
def get_structure(material_id: str, fmt: str = "json") -> dict | str:
    """Get the crystal structure for a material.

    Args:
        material_id: Materials Project ID (e.g. "mp-1234")
        fmt: Output format — "json" (default) or "cif"
    """
    with MPRester(MP_API_KEY) as mpr:
        structure = mpr.get_structure_by_material_id(material_id)
        if fmt == "cif":
            from pymatgen.io.cif import CifWriter
            return str(CifWriter(structure))
        return structure.as_dict()


@mcp.tool()
def get_dos(material_id: str) -> dict:
    """Get the density of states (DOS) for a material.

    Args:
        material_id: Materials Project ID (e.g. "mp-1234")
    """
    with MPRester(MP_API_KEY) as mpr:
        dos = mpr.get_dos_by_material_id(material_id)
        return dos.as_dict()


# ── Web search tools ─────────────────────────────────────────────────────────

@mcp.tool()
def web_search(query: str, num_results: int = 5) -> list[dict]:
    """Search the web for DFT methodology, GGA+U parameters, or materials science literature.

    Use this to look up:
    - Recommended Hubbard U values for specific elements/oxides
    - Best DFT functional for a given material class
    - FHI-aims or Quantum ESPRESSO parameter recommendations
    - Recent papers on a material or property

    Args:
        query: Search query (e.g. "GGA+U Hubbard U values Fe2O3 DFT Dudarev",
               "FHI-aims band structure k-path tutorial", "TiO2 DFT+U literature")
        num_results: Number of results to return (default 5, max 10)
    """
    from duckduckgo_search import DDGS

    num_results = min(num_results, 10)
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=num_results):
            results.append({
                "title": r["title"],
                "url": r["href"],
                "snippet": r["body"],
            })
    return results


@mcp.tool()
def fetch_documentation(url: str) -> str:
    """Fetch and return the text content of a documentation page, manual, or paper abstract.

    Use this to read:
    - FHI-aims or Quantum ESPRESSO manual pages
    - Materials Project documentation
    - arXiv abstracts or method sections
    - Tutorial pages found via web_search

    Args:
        url: Full URL to fetch (e.g. a QE input description page or arXiv abstract)
    """
    import httpx
    from bs4 import BeautifulSoup

    resp = httpx.get(
        url,
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "MAME-Agent/0.2 (computational materials science research)"},
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Trim to avoid overwhelming the context window
    if len(text) > 8000:
        text = text[:8000] + "\n\n[... content truncated at 8000 characters ...]"
    return text


# ── Local script library tools ───────────────────────────────────────────────

@mcp.tool()
def list_scripts(code: str = "", task: str = "") -> list[dict]:
    """List available DFT input file templates from the local script library.

    Args:
        code: Filter by DFT code — "fhi-aims", "quantum-espresso", "python", or "" for all
        task: Filter by task — "scf", "nscf", "geometry-optimization", "vc-relax",
              "band-structure", "dos", "plotting", "analysis", or "" for all
    """
    index_path = _SCRIPTS_DIR / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    scripts = index["scripts"]
    if code:
        scripts = [s for s in scripts if s["code"] == code]
    if task:
        scripts = [s for s in scripts if s["task"] == task]

    return [
        {
            "id": s["id"],
            "code": s["code"],
            "task": s["task"],
            "description": s["description"],
            "status": s["status"],
            "files": s.get("files", []),
        }
        for s in scripts
    ]


@mcp.tool()
def get_script(script_id: str) -> dict:
    """Return the content of a DFT input file template from the local script library.

    Use list_scripts first to discover available script IDs.

    Args:
        script_id: Script identifier (e.g. "aims-scf", "qe-vc-relax", "aims-dos")
    """
    index_path = _SCRIPTS_DIR / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    entry = next((s for s in index["scripts"] if s["id"] == script_id), None)
    if entry is None:
        available = [s["id"] for s in index["scripts"]]
        return {"error": f"Script '{script_id}' not found. Available: {available}"}

    if entry.get("status") == "placeholder":
        return {
            "id": entry["id"],
            "status": "placeholder",
            "message": f"Template '{script_id}' is not yet implemented in the library.",
        }

    target = _SCRIPTS_DIR / entry["path"]
    files = {}

    if target.is_dir():
        for fpath in sorted(target.iterdir()):
            if fpath.is_file():
                files[fpath.name] = fpath.read_text()
    elif target.is_file():
        files[target.name] = target.read_text()
    else:
        return {"error": f"Path not found on disk: {entry['path']}"}

    return {
        "id": entry["id"],
        "code": entry["code"],
        "task": entry["task"],
        "description": entry["description"],
        "files": files,
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
