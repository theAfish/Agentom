from typing import Optional
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


def search_materials_project(query: str) -> str:
    """
    Search for materials in Materials Project.
    This is a placeholder function.
    
    Args:
        query: Search query for Materials Project
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

def search_materials_by_formula(
    formula: str,
    energy_above_hull: Optional[tuple[float, float]] = None,
    is_stable: Optional[bool] = None,
    spacegroup_number: Optional[int | list[int]] = None,
    num_results: Optional[int] = None
) -> str:
    """
    Search for materials by chemical formula in Materials Project.
    This search will return materials matching the given formula, with optional filters.
    
    Args:
        formula: Chemical formula (e.g., 'Fe2O3' or 'Fe2O*' for wildcard)
        energy_above_hull: Min/max energy above hull in eV (optional)
        is_stable: Filter for stable materials on convex hull (optional)
        spacegroup_number: Spacegroup number(s) (optional)
        num_results: Maximum number of results to return
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


def search_materials_by_chemical_system(
    chemical_system: str,
    energy_above_hull: Optional[tuple[float, float]] = None,
    spacegroup_symbol: Optional[str | list[str]] = None,
    num_results: Optional[int] = None
) -> str:
    """
    Search for materials by chemical system in Materials Project.
    This search will return materials within the specified chemical system, with optional filters.
    
    Args:
        chemical_system: Chemical system (e.g., 'Fe-O' for iron-oxygen compounds)
        energy_above_hull: Min/max energy above hull in eV (optional)
        spacegroup_symbol: Spacegroup symbol(s) (optional)
        num_results: Maximum number of results to return
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


def search_materials_by_structure(
    crystal_system: str,
    spacegroup_number: Optional[int | list[int]] = None,
    elements: Optional[list[str]] = None,
    num_results: Optional[int] = None
) -> str:
    """
    Search for materials by structural properties like spacegroup.
    
    Args:
        crystal_system: Crystal system (e.g., 'cubic', 'hexagonal')
        spacegroup_number: Spacegroup number(s)
        elements: Optional elements to include
        num_results: Maximum number of results to return
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



def download_structure(mp_id: str) -> str:
    """
    Download a structure from Materials Project.
    This is a placeholder function.
    
    Args:
        mp_id: Materials Project ID (e.g., mp-1234)
    """
    # Mock download by creating a dummy file if it doesn't exist
    # In real implementation, use MPRester to get structure and write to file
    return f"Downloaded structure {mp_id} to workspace/inputs/{mp_id}.cif (Mock)"
