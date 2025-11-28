from typing import Annotated, Optional
from agent_framework import ai_function
from mp_api.client import MPRester
import os
from dotenv import load_dotenv, find_dotenv
import json

# MP_API_KEY is in the .env file, same as the OPENAI_API_KEY

# Load .env from the project (if present) so env vars like MP_API_KEY are available.
dot_env_path = find_dotenv()
if dot_env_path:
    load_dotenv(dot_env_path)
else:
    # try a default load (safe even if no .env file exists)
    load_dotenv()


def _get_mp_api_key() -> str | None:
    """Return the Materials Project API key from environment or .env, or None."""
    return os.getenv("MP_API_KEY")

@ai_function
def search_materials_project(query: Annotated[str, "Search query for Materials Project"]) -> str:
    """
    Search for materials in Materials Project.
    This is a placeholder function.
    """
    # Ensure we have an API key from environment or .env
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError(
            "MP_API_KEY not set. Please set the environment variable `MP_API_KEY` "
            "or add `MP_API_KEY=your_key` to a .env file in the project root."
        )

    # This is a mock search; in a real implementation, use mpr.query or similar.
    # Keep the MPRester context usage for when a real call is implemented.
    with MPRester(api_key=api_key) as mpr:
        pass

    return f"Searching Materials Project for: {query}. (Mock result: Found mp-1234, mp-5678)"


# search with elements
@ai_function
def search_materials_by_formula(
    formula: Annotated[str, "Chemical formula (e.g., 'Fe2O3' or 'Fe2O*' for wildcard)"],
    energy_above_hull: Annotated[Optional[tuple[float, float]], "Min/max energy above hull in eV (optional)"] = None,
    is_stable: Annotated[Optional[bool], "Filter for stable materials on convex hull (optional)"] = None,
    spacegroup_number: Annotated[Optional[int | list[int]], "Spacegroup number(s) (optional)"] = None,
    num_results: Annotated[Optional[int], "Maximum number of results to return"] = None
) -> str:
    """
    Search for materials by chemical formula in Materials Project.
    This search will return materials matching the given formula, with optional filters.
    """
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError("MP_API_KEY not set. Please set the environment variable `MP_API_KEY` "
        "or add it to a .env file in the project root.")
    
    with MPRester(api_key=api_key) as mpr:
        docs = mpr.materials.summary.search(
            formula=formula,
            energy_above_hull=energy_above_hull,
            is_stable=is_stable,
            spacegroup_number=spacegroup_number,
            fields=["material_id", "formula_pretty", "structure", "energy_above_hull"],
            num_docs=num_results
        )
    
    # Serialize results to JSON string for agent
    results = [{"material_id": doc.material_id, "formula": doc.formula_pretty, "e_hull": doc.energy_above_hull} for doc in docs]
    return json.dumps(results) if results else "No materials found."

@ai_function
def search_materials_by_chemical_system(
    chemical_system: Annotated[str, "Chemical system (e.g., 'Fe-O' for iron-oxygen compounds)"],
    energy_above_hull: Annotated[Optional[tuple[float, float]], "Min/max energy above hull in eV (optional)"] = None,
    spacegroup_symbol: Annotated[Optional[str | list[str]], "Spacegroup symbol(s) (optional)"] = None,
    num_results: Annotated[Optional[int], "Maximum number of results to return"] = None
) -> str:
    """
    Search for materials by chemical system in Materials Project.
    This search will return materials within the specified chemical system, with optional filters.
    """
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError("MP_API_KEY not set. Please set the environment variable `MP_API_KEY` "
        "or add it to a .env file in the project root.")
    
    with MPRester(api_key=api_key) as mpr:
        docs = mpr.materials.summary.search(
            chemsys=chemical_system,
            energy_above_hull=energy_above_hull,
            spacegroup_symbol=spacegroup_symbol,
            fields=["material_id", "formula_pretty", "energy_above_hull", "is_stable"],
            num_docs=num_results
        )
    
    results = [{"material_id": doc.material_id, "formula": doc.formula_pretty, "stable": doc.is_stable} for doc in docs]
    return json.dumps(results) if results else "No materials found."

@ai_function
def search_materials_by_structure(
    crystal_system: Annotated[str, "Crystal system (e.g., 'cubic', 'hexagonal')"],
    spacegroup_number: Annotated[Optional[int | list[int]], "Spacegroup number(s)"] = None,
    elements: Annotated[Optional[list[str]], "Optional elements to include"] = None,
    num_results: Annotated[Optional[int], "Maximum number of results to return"] = None
) -> str:
    """
    Search for materials by structural properties like spacegroup.
    """
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError("MP_API_KEY not set. Please set the environment variable `MP_API_KEY` "
        "or add it to a .env file in the project root.")
    
    with MPRester(api_key=api_key) as mpr:
        docs = mpr.materials.summary.search(
            spacegroup_number=spacegroup_number,
            crystal_system=crystal_system,
            elements=elements,
            fields=["material_id", "formula_pretty", "spacegroup_symbol", "density"],
            num_docs=num_results
        )
    
    results = [{"material_id": doc.material_id, "formula": doc.formula_pretty, "spacegroup": doc.spacegroup_symbol} for doc in docs]
    return json.dumps(results) if results else "No materials found."


@ai_function
def download_structure(mp_id: Annotated[str, "Materials Project ID (e.g., mp-1234)"]) -> str:
    """
    Download a structure from Materials Project.
    This is a placeholder function.
    """
    # Mock download by creating a dummy file if it doesn't exist
    # In real implementation, use MPRester to get structure and write to file
    return f"Downloaded structure {mp_id} to workspace/inputs/{mp_id}.cif (Mock)"
