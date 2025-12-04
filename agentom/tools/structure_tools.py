"""
Tools for working with ASE (Atomic Simulation Environment).
"""
from pathlib import Path
from typing import Optional
from ase import Atoms
from ase.io import read
from ase.build import surface, make_supercell
from ase.data import covalent_radii
from ase.geometry import get_distances
from ase.io import write
from ase.visualize.plot import plot_atoms
import numpy as np
import os
import matplotlib.pyplot as plt

from pymatgen.core.structure import Structure
from pymatgen.analysis.interfaces.substrate_analyzer import SubstrateAnalyzer
from pymatgen.analysis.interfaces.coherent_interfaces import CoherentInterfaceBuilder
from pymatgen.io.ase import AseAtomsAdaptor

from agentom.settings import settings


def _load_atoms(folder: str, file_name: str) -> Atoms:
    """Loads an ASE Atoms object from disk."""
    # Handle folder being "." or empty string
    if folder == "." or folder == "":
        file_path = settings.WORKSPACE_DIR / file_name
    else:
        file_path = settings.WORKSPACE_DIR / folder / file_name
        
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    return read(file_path)


def _load_atoms_from_path(path_str: str) -> Atoms:
    """Load an ASE Atoms object from a path string.

    This helper accepts either an absolute or relative filesystem path, or
    a workspace-relative path/filename. It returns the Atoms object on
    success or a dict with an "error" key on failure (to match
    _load_atoms behavior).
    """
    p = Path(path_str)

    # If the provided path exists as given (absolute or relative), use it.
    if p.exists():
        try:
            return read(p)
        except Exception as e:
            return {"error": str(e)}

    # Try interpreting the input as relative to the workspace dir
    alt = settings.WORKSPACE_DIR / path_str
    if alt.exists():
        try:
            return read(alt)
        except Exception as e:
            return {"error": str(e)}

    # If path_str looks like a filename in the workspace root, delegate
    # to the existing _load_atoms helper for consistent behavior.
    if p.parent == Path('.'):
        return _load_atoms('.', p.name)

    return {"error": f"File not found: {path_str}"}


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
        file_path = settings.WORKSPACE_DIR / file_name
    else:
        file_path = settings.WORKSPACE_DIR / folder / file_name
        
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

def build_supercell(folder: str, file_name: str, repetitions: list[int] | list[list[int]], output_name: Optional[str] = None) -> dict:
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
    output_file_path = settings.OUTPUT_DIR / output_file_name
    if not settings.OUTPUT_DIR.exists():
        os.makedirs(settings.OUTPUT_DIR)
    write(output_file_path, supercell_atoms)
    return {
        "original_file": file_name,
        "output_supercell_file": output_file_name,
    }

def build_surface(folder: str, file_name: str, miller_indices: list, layers: int, vacuum: float, output_name: Optional[str] = None) -> dict:
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
        output_file_path = settings.OUTPUT_DIR / output_file_name
        if not settings.OUTPUT_DIR.exists():
            os.makedirs(settings.OUTPUT_DIR)
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
    
    output_file_path = settings.OUTPUT_DIR / output_image_name
    if not settings.OUTPUT_DIR.exists():
        os.makedirs(settings.OUTPUT_DIR)
        
    try:
        # Use ASE's plot_atoms and matplotlib to save with custom DPI
        fig, ax = plt.subplots()
        plot_atoms(atoms, ax=ax, rotation=rotation)
        ax.axis('off')  # Remove coordinate axes
        plt.savefig(output_file_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return {
            "original_file": file_name,
            "output_image_file": str(output_file_path.relative_to(settings.WORKSPACE_DIR)),
        }
    except Exception as e:
        return {"error": str(e)}

def check_close_atoms(folder: str, file_name: str, tolerance: float = -0.5) -> dict:
    """
    Checks for atoms that are too close to each other, using covalent radii plus tolerance. 
    This tool is useful for validating structures.
    """
    atoms = _load_atoms(folder, file_name)
    if isinstance(atoms, dict) and "error" in atoms:
        return atoms
    
    positions = atoms.positions
    cell = atoms.cell
    pbc = atoms.pbc
    
    distances, indices = get_distances(positions, cell=cell, pbc=pbc)
    
    close_pairs = []
    for i in range(len(atoms)):
        for j in range(i+1, len(atoms)):
            dist_vector = distances[i, j]
            dist = float(np.linalg.norm(dist_vector))
            r1 = covalent_radii[atoms[i].number]
            r2 = covalent_radii[atoms[j].number]
            min_dist = r1 + r2 + tolerance
            if dist < min_dist:
                close_pairs.append({
                    "atom1": {
                        "index": i,
                        "symbol": atoms[i].symbol,
                    },
                    "atom2": {
                        "index": j,
                        "symbol": atoms[j].symbol,
                    },
                    "distance_angstrom": round(dist, 3),
                    "min_distance_angstrom": round(float(min_dist), 3),
                })
    num_close = len(close_pairs)
    return {
        "file": file_name,
        "number_of_detected_close_pairs": num_close,
        "close_pairs": close_pairs,
    }




def build_interface(
    film_structure: str,
    substrate_structure: str,
    film_miller: tuple = (1, 0, 0),
    substrate_miller: tuple = (1, 1, 1),
    output_file: Optional[str] = None,
    output_format: Optional[str] = "cif",
    max_area: Optional[float] = 400.0,
    max_length_tol: Optional[float] = 0.03,
    max_angle_tol: Optional[float] = 0.01,
    gap: float = 2.5,
    vacuum_over_film: Optional[float] = 0.0,
    film_thickness: int = 2,
    substrate_thickness: int = 2,
    in_layers: Optional[bool] = True
) -> dict:
    """
    Builds a coherent interface structure between a film and substrate using pymatgen,
    starting from ASE Atoms objects.

    Parameters:
    - film_structure: File path for the film material structure.
    - substrate_structure: File path for the substrate material structure.
    - film_miller: Miller index for the film surface (default: (1, 0, 0)).
    - substrate_miller: Miller index for the substrate surface (default: (1, 1, 1)).
    - output_file: Optional path to save the generated interface structure as a file.
    - max_area: Maximum supercell area for matching (default: 400.0).
    - max_length_tol: Length tolerance for ZSL matching (default: 0.03).
    - max_angle_tol: Angle tolerance for ZSL matching (default: 0.01).
    - gap: Gap between film and substrate in Å (default: 2.5).
    - vacuum_over_film: Vacuum above the film in Å (default: 0.0). If set to 0, it will be adjusted to 'gap'.
    - film_thickness: Film thickness in layers or Å (default: 1).
    - substrate_thickness: Substrate thickness in layers or Å (default: 1).
    - in_layers: If True, thickness is in number of layers (default: True).

    Returns:
    - The generated structure path or error message.
    """
    # Load structures from file paths using safer loader that handles
    # absolute paths and workspace-relative names.
    adaptor = AseAtomsAdaptor()
    try:
        film_atoms = _load_atoms_from_path(film_structure)
        substrate_atoms = _load_atoms_from_path(substrate_structure)
        film = adaptor.get_structure(film_atoms)
        substrate = adaptor.get_structure(substrate_atoms)
    except Exception as e:
        return {"error": f"Failed to load structures: {str(e)}"}
    
    # Ensure numeric parameters are of correct type
    try:
        gap = float(gap)
        if vacuum_over_film is not None:
            vacuum_over_film = float(vacuum_over_film)
        else:
            vacuum_over_film = 0.0
        
        if max_area is not None:
            max_area = float(max_area)
        if max_length_tol is not None:
            max_length_tol = float(max_length_tol)
        if max_angle_tol is not None:
            max_angle_tol = float(max_angle_tol)
            
        film_thickness = int(film_thickness)
        substrate_thickness = int(substrate_thickness)


        # Find matches using SubstrateAnalyzer with parameters directly
        analyzer = SubstrateAnalyzer(
            max_area_ratio_tol=0.09,  # Default value; adjust if needed
            max_area=max_area,
            max_length_tol=max_length_tol,
            max_angle_tol=max_angle_tol
        )
        matches = list(analyzer.calculate(
            film=film,
            substrate=substrate,
            film_millers=[film_miller],
            substrate_millers=[substrate_miller]
        ))
    except Exception as e:
        return {"error": f"Error during matching: {str(e)}"}
    
    
    if not matches:
        return {"error": "No lattice matches found. Try adjusting tolerances or Miller indices."}

    # Use the first match (lowest strain preferred)
    match = sorted(matches, key=lambda m: m.von_mises_strain)[0]

    # Initialize CoherentInterfaceBuilder without sl_vectors
    builder = CoherentInterfaceBuilder(
        film_structure=film,
        substrate_structure=substrate,
        film_miller=match.film_miller,
        substrate_miller=match.substrate_miller,
        zslgen=analyzer  # Pass the analyzer as zslgen to use the same matching parameters
    )

    # Get terminations
    terminations = builder.terminations
    if not terminations:
        return {"error": "No terminations available for the selected slabs."}

    # Use the first termination pair
    termination = terminations[0]

    # Adjust vacuum_over_film if 0 to avoid overlap across PBC
    effective_vacuum = vacuum_over_film
    if vacuum_over_film == 0:
        effective_vacuum = gap  # Set to gap to symmetrize interfaces and prevent PBC overlap

    # Generate interfaces
    interfaces = list(builder.get_interfaces(
        termination=termination,
        gap=gap,
        vacuum_over_film=effective_vacuum,
        film_thickness=film_thickness,
        substrate_thickness=substrate_thickness,
        in_layers=in_layers
    ))

    if not interfaces:
        return{"error": "No interfaces generated. Check parameters."}

    # Return the first interface
    interface = interfaces[0]

    # Optional adjustments
    interface.translate_sites(range(len(interface)), [0, 0, 0])  # Translate for better visualization

    if output_file:
        output_path = settings.OUTPUT_DIR / output_file
    else:
        # get the names of the input files without extensions
        film_name = Path(film_structure).stem
        substrate_name = Path(substrate_structure).stem
        output_path = settings.OUTPUT_DIR / f"{film_name}-{substrate_name}_interface.{output_format}"
    
    try:
        interface.to(output_path, output_format)
    except Exception as e:
        return {"error": f"Failed to write interface to file: {str(e)}"}

    return {
        "output_interface_file": str(output_path.relative_to(settings.WORKSPACE_DIR)),
    }