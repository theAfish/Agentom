from typing import Optional
from mp_api.client import MPRester
import os
from dotenv import load_dotenv, find_dotenv
import json
from pathlib import Path

from ase import Atoms
from pymatgen.core.structure import Structure
from pymatgen.io.ase import AseAtomsAdaptor

from agentom.config import BASE_DIR, WORKSPACE_DIR, OUTPUT_DIR, TEMP_DIR


IMPORTANT_FIELDS = [
    "material_id", 
    "formula_pretty", 
    "energy_above_hull", 
    "is_stable", 
    "symmetry", 
    "structure", 
    "nelements", 
    "nsites"
]

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


# Under construction
def _save_docs_to_json(docs: list, filename: str) -> Path:
    results = [{
        "mpid": doc.material_id, 
        "formula": doc.formula_pretty, 
        "e_hull": doc.energy_above_hull,
        "is_stable": doc.is_stable,
        "crystal_system": doc.symmetry.crystal_system,
        "spacegroup_symbol": doc.symmetry.symbol,
        "num_elements": doc.nelements,
        "num_sites": doc.nsites,
        "structure": doc.structure.as_dict()
    } for doc in docs]

    file_path = TEMP_DIR / filename
    docs_info = {
        "num_results": len(results),
        "relative_path": file_path.relative_to(WORKSPACE_DIR),
    }
    with open(file_path, "w") as f:
        json.dump(results, f, default=str)
    return docs_info

def _save_dict_to_file(structure_dict: dict, file_name: str = None, target_format: str = "cif"):
    # Convert dict to pymatgen Structure
    pmg_structure = Structure.from_dict(structure_dict)
    # save to the target format using pymatgen's built-in writers
    if file_name is None:
        prefix = structure_dict.get("material_id", "structure")
        file_name = f"{prefix}.{target_format}"
    else:
        file_name = f"{file_name}.{target_format}"
    full_path = OUTPUT_DIR / file_name
    pmg_structure.to(filename=full_path)
    relative_path = full_path.relative_to(WORKSPACE_DIR)
    return relative_path

# search with elements

def search_materials_by_formula(
    formula: str,
    min_energy_above_hull: Optional[float] = None,
    max_energy_above_hull: Optional[float] = None,
    is_stable: Optional[bool] = None,
    spacegroup_number: Optional[int | list[int]] = None,
    num_results: Optional[int] = None
) -> str:
    """
    Search for materials by chemical formula in Materials Project.
    This search will return materials matching the given formula, with optional filters.
    
    Args:
        formula: Chemical formula (e.g., 'Fe2O3' or 'Fe2O*' for wildcard)
        min_energy_above_hull: Minimum energy above hull in eV (optional)
        max_energy_above_hull: Maximum energy above hull in eV (optional)
        is_stable: Filter for stable materials on convex hull (optional)
        spacegroup_number: Spacegroup number(s) (optional)
        num_results: Maximum number of results to return
    """
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError("MP_API_KEY not set. Please set the environment variable `MP_API_KEY` "
        "or add it to a .env file in the project root.")
    
    energy_above_hull = None
    if min_energy_above_hull is not None and max_energy_above_hull is not None:
        energy_above_hull = (min_energy_above_hull, max_energy_above_hull)
    
    with MPRester(api_key=api_key) as mpr:
        docs = mpr.materials.summary.search(
            formula=formula,
            energy_above_hull=energy_above_hull,
            is_stable=is_stable,
            spacegroup_number=spacegroup_number,
            fields=IMPORTANT_FIELDS,
        )

        if num_results is not None:
            docs = docs[:num_results]
    
    # # Serialize results to JSON string for agent
    # results = [{"mpid": doc.material_id, "formula": doc.formula_pretty, "e_hull": doc.energy_above_hull, "structure": doc.structure.as_dict()} for doc in docs]
    # # store the results in the tmp folder inside the workspace of agent for later retrieval
    # file_path = TEMP_DIR / f'mp_search_{formula.replace("*", "X")}.json'
    # with open(file_path, "w") as f:
    #     json.dump(results, f, default=str)

    docs_info = _save_docs_to_json(docs, f'mp_search_{formula.replace("*", "X")}.json')
    # Return only string information for agent, rather than the raw results since they may contain complex objects
    relative_path = docs_info["relative_path"]
    to_agent_info = f"Found {docs_info['num_results']} materials matching formula {formula}. "
    to_agent_info += f"The results are stored in {relative_path} for further analysis."
    return to_agent_info


def search_materials_by_chemical_system(
    chemical_system: str,
    min_energy_above_hull: Optional[float] = None,
    max_energy_above_hull: Optional[float] = None,
    spacegroup_symbol: Optional[str | list[str]] = None,
    num_results: Optional[int] = None
) -> str:
    """
    Search for materials by chemical system in Materials Project.
    This search will return materials within the specified chemical system, with optional filters.
    
    Args:
        chemical_system: Chemical system (e.g., 'Fe-O' for iron-oxygen compounds)
        min_energy_above_hull: Minimum energy above hull in eV (optional)
        max_energy_above_hull: Maximum energy above hull in eV (optional)
        spacegroup_symbol: Spacegroup symbol(s) (optional)
        num_results: Maximum number of results to return
    """
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError("MP_API_KEY not set. Please set the environment variable `MP_API_KEY` "
        "or add it to a .env file in the project root.")
    
    energy_above_hull = None
    if min_energy_above_hull is not None and max_energy_above_hull is not None:
        energy_above_hull = (min_energy_above_hull, max_energy_above_hull)
    
    with MPRester(api_key=api_key) as mpr:
        docs = mpr.materials.summary.search(
            chemsys=chemical_system,
            energy_above_hull=energy_above_hull,
            spacegroup_symbol=spacegroup_symbol,
            fields=IMPORTANT_FIELDS,
        )
        if num_results is not None:
            docs = docs[:num_results]

    docs_info = _save_docs_to_json(docs, f'mp_search_{chemical_system.replace("-", "_")}.json')
    relative_path = docs_info["relative_path"]
    to_agent_info = f"Found {docs_info['num_results']} materials in chemical system {chemical_system}. "
    to_agent_info += f"The results are stored in {relative_path} for further analysis."    
    return to_agent_info


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
        )

        if num_results is not None:
            docs = docs[:num_results]
    
    results = [{"material_id": doc.material_id, "formula": doc.formula_pretty, "spacegroup": doc.spacegroup_symbol} for doc in docs]
    return json.dumps(results) if results else "No materials found."




if __name__ == "__main__":
    # debug the search functions
    # print(search_materials_by_formula("H2O", min_energy_above_hull=0, max_energy_above_hull=5.0, is_stable=False, num_results=5))
    # print(search_materials_by_chemical_system("Fe-O", min_energy_above_hull=0, max_energy_above_hull=2.0, spacegroup_symbol=["Fm-3m"], num_results=5))

    pass
