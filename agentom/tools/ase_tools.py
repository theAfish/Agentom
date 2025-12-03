"""
Tools for working with ASE (Atomic Simulation Environment).
"""
from pathlib import Path
from typing import Optional
from ase import Atoms
from ase.io import read
from ase.build import surface, make_supercell
from ase.io import write
import numpy as np
import os
import subprocess
import sys
import matplotlib.pyplot as plt
from ase.visualize.plot import plot_atoms

from agentom.config import BASE_DIR, WORKSPACE_DIR, OUTPUT_DIR


def list_all_files():
    """Lists all files available in the workspace directory, in a tree-like structure, with their relative subfolder paths as keys."""
    if not WORKSPACE_DIR.exists():
        return {"files": []}
    files = {}
    for path in WORKSPACE_DIR.rglob("*"):
        if path.is_file():
            try:
                subfolder = path.parent.relative_to(WORKSPACE_DIR)
                files.setdefault(str(subfolder), []).append(path.name)
            except ValueError:
                # Handle case where path is not relative to WORKSPACE_DIR (should not happen with rglob)
                pass
    return {"files": files}


def _load_atoms(folder: str, file_name: str) -> Atoms:
    """Loads an ASE `Atoms` object from disk."""
    # Handle folder being "." or empty string
    if folder == "." or folder == "":
        file_path = WORKSPACE_DIR / file_name
    else:
        file_path = WORKSPACE_DIR / folder / file_name
        
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    return read(file_path)


def read_structure(folder: str, file_name: str) -> dict:
    """Summarizes the structure in a way that downstream agents can consume."""
    atoms = _load_atoms(folder, file_name)
    if isinstance(atoms, dict) and "error" in atoms:
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

def read_structures_in_text(folder: str, file_name: str) -> dict:
    """Read the raw structure file in text format as a string, if agents want to see and check."""
    if folder == "." or folder == "":
        file_path = WORKSPACE_DIR / file_name
    else:
        file_path = WORKSPACE_DIR / folder / file_name
        
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    return {"raw_file_text": open(file_path, 'r').read()}


def calculate_distance(folder: str, file_name: str, index1: int, index2: int) -> dict:
    """Calculates the distance between two atoms within the referenced structure."""
    atoms = _load_atoms(folder, file_name)
    if isinstance(atoms, dict) and "error" in atoms:
        return atoms
        
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

def generate_structure_image(folder: str, file_name: str, output_image_name: str, rotation: str = '', dpi: int = 100) -> dict:
    """Generates an image of the structure using ASE.
    rotation: string like '10x,20y,30z'
    dpi: resolution in dots per inch for the PNG image
    """
    atoms = _load_atoms(folder, file_name)
    if isinstance(atoms, dict) and "error" in atoms:
        return atoms
    
    output_file_path = OUTPUT_DIR / output_image_name
    if not OUTPUT_DIR.exists():
        os.makedirs(OUTPUT_DIR)
        
    try:
        # Use ASE's plot_atoms and matplotlib to save with custom DPI
        fig, ax = plt.subplots()
        plot_atoms(atoms, ax=ax, rotation=rotation)
        ax.axis('off')  # Remove coordinate axes
        plt.savefig(output_file_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return {
            "original_file": file_name,
            "output_image_file": str(output_file_path.relative_to(WORKSPACE_DIR)),
        }
    except Exception as e:
        return {"error": str(e)}

def run_python_script(script_name: str) -> dict:
    """Runs a Python script in the workspace using Docker for safety."""
    
    # script_name should be relative to WORKSPACE_DIR
    script_path = WORKSPACE_DIR / script_name
    
    # Resolve the path to handle symlinks, relative components, etc.
    try:
        resolved_path = script_path.resolve()
    except Exception as e:
        return {"error": f"Failed to resolve script path: {str(e)}"}
    
    # Ensure the script is within the workspace to prevent path traversal
    if not resolved_path.is_relative_to(WORKSPACE_DIR):
        return {"error": "Script path is outside the workspace"}
    
    if not resolved_path.exists():
        return {"error": f"File not found: {resolved_path}"}
    
    try:
        # Build the Docker image if not already built
        image_name = "agentom-runner"
        build_result = subprocess.run(
            ["docker", "build", "-t", image_name, "."],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )
        if build_result.returncode != 0:
            return {"error": f"Failed to build Docker image: {build_result.stderr}"}
        
        # Run the script in Docker
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{WORKSPACE_DIR}:/workspace", "-w", "/workspace", image_name, "python", script_name],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        return {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}