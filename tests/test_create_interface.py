from pathlib import Path
import os
from ase import Atoms
from ase.io import write, read
from agentom.tools.structure_tools import create_interface
from agentom.settings import settings


def test_create_interface_basic():
    # Prepare workspace and output directories
    ws = Path(settings.WORKSPACE_DIR)
    out_dir = Path(settings.OUTPUT_DIR)
    ws.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Create a simple bottom structure (single Cu atom)
    bottom = Atoms('Cu', positions=[[0.0, 0.0, 0.0]],
                   cell=[[3.6, 0.0, 0.0], [0.0, 3.6, 0.0], [0.0, 0.0, 10.0]],
                   pbc=[True, True, True])
    # Create a simple top structure (single O atom) with the same lateral cell
    top = Atoms('O', positions=[[1.0, 1.0, 0.0]],
                cell=[[3.6, 0.0, 0.0], [0.0, 3.6, 0.0], [0.0, 0.0, 5.0]],
                pbc=[True, True, True])

    bottom_file = ws / 'bottom_test.cif'
    top_file = ws / 'top_test.cif'
    write(bottom_file, bottom)
    write(top_file, top)

    # Create interface with a requested separation
    separation = 3.0
    res = create_interface('.', 'top_test.cif', 'bottom_test.cif', separation=separation, output_name='interface_test.cif')

    assert 'error' not in res, f"create_interface returned an error: {res.get('error')}"
    assert res.get('output_interface_file') == 'interface_test.cif'

    out_path = out_dir / 'interface_test.cif'
    assert out_path.exists(), f"Expected output file not found: {out_path}"

    # Read combined structure and check z separation between the two atoms
    combined = read(out_path)
    zs = sorted([float(p[2]) for p in combined.positions])
    assert len(zs) >= 2, "Combined structure should contain at least two atoms"
    actual_sep = zs[-1] - zs[0]
    assert actual_sep + 1e-6 >= separation, f"Separation too small: {actual_sep} < {separation}"
