from ase import Atoms
from ase.io import write

# Create a BCC (Body-Centered Cubic) Nickel structure
# Lattice parameter for BCC Ni is approximately 3.52 A (though note that 
# Ni is actually FCC in its ground state, but we'll create BCC as requested)

# For BCC structure, we have atoms at (0,0,0) and (0.5,0.5,0.5)
bcc_ni = Atoms('Ni2',
               positions=[[0, 0, 0], [0.5, 0.5, 0.5]],
               cell=[3.52, 3.52, 3.52],
               pbc=True)

# Write the structure to a file
write('bcc_Ni.cif', bcc_ni)
print("BCC Nickel structure has been generated and saved as 'bcc_Ni.cif'")