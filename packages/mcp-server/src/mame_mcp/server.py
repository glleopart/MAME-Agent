"""MAME MCP Server — exposes Materials Project data as MCP tools."""

import os
from mcp.server.fastmcp import FastMCP
from mp_api.client import MPRester
from dotenv import load_dotenv

load_dotenv()

MP_API_KEY = os.getenv("MP_API_KEY")

mcp = FastMCP("mame-mcp")


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


def main():
    mcp.run()


if __name__ == "__main__":
    main()
