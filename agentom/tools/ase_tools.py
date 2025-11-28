"""
Tools for working with ASE (Atomic Simulation Environment).
"""
from pathlib import Path
from typing import Optional, Annotated
from ase import Atoms
from ase.io import read
from ase.build import surface, make_supercell
from ase.io import write
import numpy as np
import os

from pydantic import Field
from agent_framework import ai_function

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
OUTPUT_DIR = WORKSPACE_DIR / "outputs"


@ai_function(name="list_all_files", description="Lists all files available in the workspace directory, in a tree-like structure, with their relative subfolder paths as keys.")
def list_all_files():
    """Lists all files available in the workspace directory, in a tree-like structure, with their relative subfolder paths as keys."""
    if not WORKSPACE_DIR.exists():
        return {"files": []}
    files = {}
    for path in WORKSPACE_DIR.rglob("*"):
        if path.is_file():
            subfolder = path.parent.relative_to(WORKSPACE_DIR)
            files.setdefault(str(subfolder), []).append(path.name)
    return {"files": files}


def _load_atoms(folder: str, file_name: str) -> Atoms:
    """Loads an ASE `Atoms` object from disk."""
    file_path = WORKSPACE_DIR / folder / file_name
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    return read(file_path)


@ai_function(name="read_structure", description="Summarizes the structure in a way that downstream agents can consume.")
def read_structure(folder: str, file_name: str) -> dict:
    """Summarizes the structure in a way that downstream agents can consume."""
    atoms = _load_atoms(folder, file_name)
    if "error" in atoms:
        return {"error": atoms["error"]}
    return {
        "file": file_name,
        "chemical_formula": atoms.get_chemical_formula(),
        "num_atoms": len(atoms),
        "atoms": [
            {
                "index": index,
                "symbol": atom.symbol,
                "position_angstrom": atoms.positions[index].tolist(),
            }
            for index, atom in enumerate(atoms)
        ],
        "cell_vectors_angstrom": atoms.cell.array.tolist()
        if atoms.cell is not None
        else None,
        "periodic_boundary_conditions": atoms.pbc.tolist(),
    }

@ai_function(name="read_structures_in_text", description="Read the raw structure file in text format as a string, if agents want to see and check.")
def read_structures_in_text(folder: str, file_name: str) -> dict:
    """Read the raw structure file in text format as a string, if agents want to see and check."""
    file_path = WORKSPACE_DIR / folder / file_name
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    return {"raw_file_text": open(file_path, 'r').read()}


@ai_function(name="calculate_distance", description="Calculates the distance between two atoms within the referenced structure.")
def calculate_distance(folder: str, file_name: str, index1: int, index2: int) -> dict:
    """Calculates the distance between two atoms within the referenced structure."""
    atoms = _load_atoms(folder, file_name)
    num_atoms = len(atoms)
    for requested_index in (index1, index2):
        if requested_index < 0 or requested_index >= num_atoms:
            return {"error": f"Atom index {requested_index} is out of bounds for {num_atoms} atoms"}

    pos1 = atoms.positions[index1]
    pos2 = atoms.positions[index2]
    distance = float(np.linalg.norm(pos1 - pos2))
    return {
        "file": file_name,
        "atom1": {
            "index": index1,
            "symbol": atoms[index1].symbol,
            "position_angstrom": pos1.tolist(),
        },
        "atom2": {
            "index": index2,
            "symbol": atoms[index2].symbol,
            "position_angstrom": pos2.tolist(),
        },
        "distance_angstrom": distance,
    }

@ai_function(name="supercell_generation", description="Generates a supercell from the given structure by repeating it along each axis.")
def supercell_generation(folder: str, file_name: str, repetitions: list[int] | list[list[int]], output_name: Optional[str] = None) -> dict:
    """Generates a supercell from the given structure by repeating it along each axis."""
    atoms = _load_atoms(folder, file_name)
    if isinstance(atoms, dict) and "error" in atoms:
        return atoms
    if len(repetitions) != 3:
        return {"error": "Repetitions must be a list of three integers, or a 3x3 matrix."}
    
    # if repetitions is a list of three integers, convert to a diagonal matrix
    if all(isinstance(x, int) for x in repetitions):
        repetitions = np.diag(repetitions)

    supercell_atoms = make_supercell(atoms, repetitions)
    if output_name:
        output_file_name = output_name
    else:
        output_file_name = f"supercell_{file_name}"
    output_file_path = OUTPUT_DIR / output_file_name
    if not OUTPUT_DIR.exists():
        os.makedirs(OUTPUT_DIR)
    write(output_file_path, supercell_atoms)
    return {
        "original_file": file_name,
        "output_supercell_file": output_file_name,
    }

@ai_function(name="create_surface_slab", description="Creates a surface slab from a bulk structure.")
def create_surface_slab(folder: str, file_name: str, miller_indices: list, layers: int, vacuum: float, output_name: Optional[str] = None) -> dict:
    """Creates a surface slab from a bulk structure."""
    try:
        atoms = _load_atoms(folder, file_name)
        if isinstance(atoms, dict) and "error" in atoms:
            return atoms
        if len(miller_indices) != 3:
            return {"error": "Miller indices must be a list of three integers."}
        
        # Pass the vacuum directly to `surface` so the returned slab keeps a valid 3D cell.
        slab = surface(atoms, miller_indices, layers, vacuum=vacuum)
        if output_name:
            output_file_name = output_name
        else:
            output_file_name = f"slab_{file_name}"
        output_file_path = OUTPUT_DIR / output_file_name
        if not OUTPUT_DIR.exists():
            os.makedirs(OUTPUT_DIR)
        write(output_file_path, slab)
        return {
            "original_file": file_name,
            "output_surface_file": output_file_name,
        }
    except Exception as e:
        return {"error": str(e)}
    
