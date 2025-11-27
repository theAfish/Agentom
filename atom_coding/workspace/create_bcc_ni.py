from ase import Atoms
from ase.build import bulk
from ase.io import write

# Create BCC nickel structure with lattice parameter 3.52 A
bcc_Ni = bulk('Ni', 'bcc', a=3.52)

# Save as CIF file
write('bcc_Ni_corrected.cif', bcc_Ni)

print("BCC nickel structure created successfully!")
print(f"Number of atoms: {len(bcc_Ni)}")
print(f"Lattice parameter: {bcc_Ni.cell.cellpar()[0]:.3f} A")
print(f"Crystal structure: {bcc_Ni.get_chemical_formula()}")