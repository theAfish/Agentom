from ase import Atoms
from ase.io import write
import numpy as np

# Create conventional BCC unit cell with lattice parameter 3.52 A
a = 3.52
bcc_Ni = Atoms(
    symbols=['Ni', 'Ni'],
    positions=[[0, 0, 0], [a/2, a/2, a/2]],
    cell=[a, a, a],
    pbc=True
)

# Save as CIF file
write('bcc_Ni_corrected.cif', bcc_Ni)

print("BCC nickel structure created successfully!")
print(f"Number of atoms: {len(bcc_Ni)}")
print(f"Lattice parameter: {bcc_Ni.cell.cellpar()[0]:.3f} A")
print(f"Crystal structure: {bcc_Ni.get_chemical_formula()}")
print(f"Atomic positions:")
for i, pos in enumerate(bcc_Ni.positions):
    print(f"  Atom {i}: {pos}")