from typing import Optional
from mp_api.client import MPRester
import os
from dotenv import load_dotenv, find_dotenv
import json
from pathlib import Path

from ase import Atoms
from pymatgen.core.structure import Structure
from pymatgen.io.ase import AseAtomsAdaptor

from agentom.settings import settings


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

    file_path = settings.TEMP_DIR / filename
    docs_info = {
        "num_results": len(results),
        "relative_path": file_path.relative_to(settings.WORKSPACE_DIR),
    }
    with open(file_path, "w") as f:
        json.dump(results, f, default=str)
    return docs_info

def _save_dict_to_file(structure_dict: dict, file_name: str = None, target_format: str = "cif"):
    # Convert dict to pymatgen Structure
    pmg_structure = Structure.from_dict(structure_dict)
    # save to the target format using pymatgen's built-in writers
    if file_name is None:
        prefix = structure_dict.get("label", "structure")
        file_name = f"{prefix}.{target_format}"
    else:
        file_name = f"{file_name}.{target_format}"
    full_path = settings.OUTPUT_DIR / file_name
    pmg_structure.to(filename=full_path)
    relative_path = full_path.relative_to(settings.WORKSPACE_DIR)
    return relative_path

# search with elements

def search_materials_by_formula(
    formula: str,
    min_energy_above_hull: Optional[float] = None,
    max_energy_above_hull: Optional[float] = None,
    is_stable: Optional[bool] = None,
    spacegroup_number: Optional[int | list[int]] = None
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
    spacegroup_symbol: Optional[str | list[str]] = None
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

    docs_info = _save_docs_to_json(docs, f'mp_search_{chemical_system.replace("-", "_")}.json')
    relative_path = docs_info["relative_path"]
    to_agent_info = f"Found {docs_info['num_results']} materials in chemical system {chemical_system}. "
    to_agent_info += f"The results are stored in {relative_path} for further analysis."    
    return to_agent_info


def search_materials_by_symmetry(
    crystal_system: str,
    spacegroup_number: Optional[int | list[int]] = None,
    elements: Optional[list[str]] = None
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
            fields=IMPORTANT_FIELDS,
        )
    
    docs_info = _save_docs_to_json(docs, f'mp_search_structure_{crystal_system}.json')
    relative_path = docs_info["relative_path"]
    to_agent_info = f"Found {docs_info['num_results']} materials with crystal system {crystal_system}. "
    to_agent_info += f"The results are stored in {relative_path} for further analysis."
    return to_agent_info

def view_data_file(file_path: str, view_types: list[str], lines: int) -> str:
    """Briefly view the contents of a data file (JSON) stored in the workspace.
    
    Args:
        file_path: Relative path to the data file
        view_types: Types of viewing for each entry. Available types: ['mpid', 'formula', 'e_hull', 'is_stable', 'crystal_system', 'spacegroup_symbol', 'num_elements', 'num_sites'] 
        lines: Number of entries to view from top
    """
    full_path = settings.WORKSPACE_DIR / file_path
    if not full_path.exists():
        return f"Error: File not found at {full_path}"
    
    try:
        with open(full_path, "r") as f:
            data = json.load(f)
        viewable_fields = ['mpid', 'formula', 'e_hull', 'is_stable', 'crystal_system', 'spacegroup_symbol', 'num_elements', 'num_sites']
        for vt in view_types:
            if vt not in viewable_fields:
                return f"Error: Unsupported view type '{vt}'. Supported types are: {viewable_fields}"
        # get the viewable info in a csv-like string
        output_lines = []
        header = "Index, " + ", ".join(view_types)
        output_lines.append(header)
        for i, entry in enumerate(data):
            line = [str(i)]
            for vt in view_types:
                line.append(str(entry.get(vt, "N/A")))
            output_lines.append(", ".join(line))
            if i + 1 >= lines:
                break
        return "\n".join(output_lines)
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
def convert_all_data_to_structure_files(
    data_file: str,
    target_format: str = "cif"
) -> str:
    """Convert all structures in a data file to specified structure files (e.g., CIF).
    
    Args:
        data_file: Relative path to the data file (JSON)
        target_format: Target structure file format (default: 'cif')
    """
    full_path = settings.WORKSPACE_DIR / data_file
    if not full_path.exists():
        return f"Error: File not found at {full_path}"
    
    try:
        with open(full_path, "r") as f:
            data = json.load(f)
        
        saved_files = []
        for entry in data:
            structure_dict = entry.get("structure")
            file_name = entry.get("mpid", None)
            if structure_dict is None:
                continue
            relative_path = _save_dict_to_file(structure_dict, target_format=target_format, file_name=file_name)
            saved_files.append(str(relative_path))
        
        return f"Converted and saved {len(saved_files)} structures to {target_format} files under {settings.OUTPUT_DIR.relative_to(settings.WORKSPACE_DIR)}."
    except Exception as e:
        return f"Error processing file: {str(e)}"
    
def convert_one_datus_to_structure_file(
    data_file: str,
    index: int,
    target_format: str = "cif"
) -> str:
    """Convert one structure in a data file to specified structure file (e.g., CIF).
    
    Args:
        data_file: Relative path to the data file (JSON)
        index: Index of the structure entry to convert (0-based)
        target_format: Target structure file format (default: 'cif')
    """
    full_path = settings.WORKSPACE_DIR / data_file
    if not full_path.exists():
        return f"Error: File not found at {full_path}"
    
    try:
        with open(full_path, "r") as f:
            data = json.load(f)
        
        if index < 0 or index >= len(data):
            return f"Error: Index {index} out of range. File contains {len(data)} entries."
        
        entry = data[index]
        structure_dict = entry.get("structure")
        file_name = entry.get("mpid", None)
        if structure_dict is None:
            return f"Error: No structure found in entry at index {index}."
        
        relative_path = _save_dict_to_file(structure_dict, target_format=target_format, file_name=file_name)
        return f"Converted and saved structure at index {index} to {relative_path}."
    except Exception as e:
        return f"Error processing file: {str(e)}"


def sample_data_from_json(data_file: str, **filters) -> str:
    """
    Sample/filter data from a JSON dataset based on target properties.
    
    Args:
        data_file: Relative path to the data file (JSON)
        **filters: Keyword arguments for filtering, e.g., crystal_system='cubic', num_sites=10
                  Supports exact matches for the specified fields.
                  Available fields: ['mpid', 'formula', 'e_hull', 'is_stable', 'crystal_system', 'spacegroup_symbol', 'num_elements', 'num_sites']
    
    Returns:
        A string summary of the sampling results.
    """
    full_path = settings.WORKSPACE_DIR / data_file
    if not full_path.exists():
        return f"Error: File not found at {full_path}"
    
    try:
        with open(full_path, "r") as f:
            data = json.load(f)
        
        # Filter the data based on provided filters
        filtered_data = []
        for entry in data:
            match = True
            for key, value in filters.items():
                if key not in entry or entry[key] != value:
                    match = False
                    break
            if match:
                filtered_data.append(entry)
        
        if not filtered_data:
            return f"No materials matched the specified filters in {data_file}."
        
        # Save filtered data to a new JSON file
        original_stem = Path(data_file).stem
        sampled_filename = f"sampled_{original_stem}.json"
        sampled_path = settings.TEMP_DIR / sampled_filename
        with open(sampled_path, "w") as f:
            json.dump(filtered_data, f, default=str)
        
        relative_path = sampled_path.relative_to(settings.WORKSPACE_DIR)
        return f"Sampled {len(filtered_data)} materials matching the filters. Results saved to {relative_path}."
    
    except Exception as e:
        return f"Error processing file: {str(e)}"
