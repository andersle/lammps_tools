"""Read data from a LAMMPS data file."""
import sys

# Format for GROMACS gro files:
_GRO_FMT = [
    ('{:5d}', 5),
    ('{:5s}', 5),
    ('{:5s}', 5),
    ('{:5d}', 5),
    ('{:8.3f}', 8),
    ('{:8.3f}', 8),
    ('{:8.3f}', 8),
]
_GRO_BOX_FMT = '{:15.9f}'

# Sections of data file with topology information:
TOPOLOGY_INFO = {
    'atoms',
    'bonds',
    'angles',
    'dihedrals',
    'impropers',
    'atom types',
    'bond types',
    'angle types',
    'dihedral types',
    'improper types',
}

# Other sections of the data file:
SECTIONS = {
    'Masses',
    'Pair Coeffs',
    'Bond Coeffs',
    'Angle Coeffs',
    'Dihedral Coeffs',
    'Improper Coeffs'
    'Nonbond Coeffs',
    'BondBond Coeffs',
    'BondAngle Coeffs',
    'MiddleBondTorsion Coeffs',
    'EndBondTorsion Coeffs',
    'AngleTorsion Coeffs',
    'AngleAngleTorsion Coeffs',
    'BondBond13 Coeffs',
    'AngleAngle Coeffs',
    'Atoms',
    'Velocities',
    'Bonds',
    'Angles',
    'Dihedrals',
    'Impropers',
}

# Formats for reading data sections:
FORMATS = {
    'atoms': [int, int, int, float, float, float, float, int, int, int],
    'velocities': [int, float, float, float],
    'bonds': [int, int, int, int],
    'angles': [int, int, int, int, int],
    'dihedrals': [int, int, int, int, int, int],
    'impropers': [int, int, int, int, int, int],
}

# For guessing atoms from masses:
PERIODIC_TABLE = {
    'H': 1.007975, 'He': 4.002602, 'Li': 6.9675, 'Be': 9.0121831,
    'B': 10.8135, 'C': 12.0106, 'N': 14.006855, 'O': 15.9994,
    'F': 18.998403163, 'Ne': 20.1797, 'Na': 22.98976928, 'Mg': 24.3055,
    'Al': 26.9815385, 'Si': 28.085, 'P': 30.973761998, 'S': 32.0675,
    'Cl': 35.4515, 'Ar': 39.948, 'K': 39.0983, 'Ca': 40.078,
    'Sc': 44.955908, 'Ti': 47.867, 'V': 50.9415, 'Cr': 51.9961,
    'Mn': 54.938044, 'Fe': 55.845, 'Co': 58.933194, 'Ni': 58.6934,
    'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723, 'Ge': 72.63, 'As': 74.921595,
    'Se': 78.971, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.4678, 'Sr': 87.62,
    'Y': 88.90584, 'Zr': 91.224, 'Nb': 92.90637, 'Mo': 95.95, 'Ru': 101.07,
    'Rh': 102.9055, 'Pd': 106.42, 'Ag': 107.8682, 'Cd': 112.414, 'In': 114.818,
    'Sn': 118.71, 'Sb': 121.76, 'Te': 127.6, 'I': 126.90447, 'Xe': 131.293,
    'Cs': 132.90545196, 'Ba': 137.327, 'La': 138.90547, 'Ce': 140.116,
    'Pr': 140.90766, 'Nd': 144.242, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25,
    'Tb': 158.92535, 'Dy': 162.5, 'Ho': 164.93033, 'Er': 167.259,
    'Tm': 168.93422, 'Yb': 173.045, 'Lu': 174.9668, 'Hf': 178.49,
    'Ta': 180.94788, 'W': 183.84, 'Re': 186.207, 'Os': 190.23, 'Ir': 192.217,
    'Pt': 195.084, 'Au': 196.966569, 'Hg': 200.592, 'Tl': 204.3835,
    'Pb': 207.2, 'Bi': 208.9804, 'Th': 232.0377, 'Pa': 231.03588,
    'U': 238.02891
}


def read_first_number(line):
    """Get the first number from a line."""
    try:
        return int(line.split()[0])
    except ValueError:
        return None


def look_for_topology_info(line, topology):
    """Look for topology info and update topology if found."""
    for key in TOPOLOGY_INFO:
        if line.find(key) != -1:
            try:
                new_key = key.replace(' ', '_')
                new_key = f'{new_key}_number'
                topology[new_key] = int(line.split()[0])
                return True
            except ValueError:
                pass
    return False


def look_for_box_info(line, topology):
    """Look for box dimensions."""
    for i in ('x', 'y', 'z'):
        low = f'{i}lo'
        high = f'{i}hi'
        length = f'l{i}'
        if line.find(low) != -1:
            if 'box' not in topology:
                topology['box'] = {}
            limit = [float(j) for j in line.split()[:2]]
            topology['box'][low] = min(limit)
            topology['box'][high] = max(limit)
            topology['box'][length] = (
                topology['box'][high] - topology['box'][low]
            )


def look_for_section(line):
    """Look for one of the sections in a line of text."""
    for key in SECTIONS:
        if line.startswith(key):
            return key
    return None


def get_molecules(topology):
    """Group atoms into molecules."""
    if 'atoms' not in topology:
        return None
    molecules = {}
    for atom in topology['atoms']:
        idx, mol_id, atom_type, charge = atom[0], atom[1], atom[2], atom[3]
        if mol_id not in molecules:
            molecules[mol_id] = {'atoms': [], 'types': [], 'charge': []}
        molecules[mol_id]['atoms'].append(idx)
        molecules[mol_id]['types'].append(atom_type)
        molecules[mol_id]['charge'].append(charge)
    return molecules


def get_atom_table(topology):
    """Convert the atom information to a dictionary."""
    if 'atoms' not in topology:
        return None
    atoms = {}
    for atom in topology['atoms']:
        atoms[atom[0]] = atom
    return atoms


def apply_format_gro(*data):
    """Apply the GROMACS format to the given data.

    Here we make sure that no strings are longer than they should be.
    """
    string = []
    for (fmti, maxlen), datai in zip(_GRO_FMT, data):
        tmp = fmti.format(datai)
        if len(tmp) > maxlen:
            tmp = tmp[:maxlen]
        string.append(tmp)
    return ''.join(string)


def write_gro_file(outputfile, topology, atom_names=None):
    """Create a gro file from the topology."""

    atom_table = get_atom_table(topology)

    if atom_names is None:
        atom_names = {}

    with open(outputfile, 'w') as output:
        output.write('Converted from LAMMPS data\n')
        output.write(f'{len(atom_table)}\n')
        for key in sorted(atom_table.keys()):
            _, mol_idx, atom_type = atom_table[key][:3]
            xyz = [i * 0.1 for i in atom_table[key][4:7]]
            atom_name = atom_names.get(atom_type, str(atom_type))
            buff = apply_format_gro(
                mol_idx,
                'MOL',
                atom_name,
                key,
                xyz[0],
                xyz[1],
                xyz[2],
            )
            output.write(f'{buff}\n')
        box = topology.get('box', None)
        if box is not None:
            box_length = [0.1 * box[i] for i in ('lx', 'ly', 'lz')]
            box_str = ' '.join([_GRO_BOX_FMT.format(i) for i in box_length])
            output.write(f'{box_str}\n')


def check_topology_consistency(topology):
    """Do some consistency checks for the topology."""
    # Things that should have equal length:
    consistency = [
        ('atoms_number', 'atoms'),
        ('atoms_number', 'velocities'),
        ('atom_types_number', 'masses'),
        ('atom_types_number', 'pair_coeffs'),
        ('bonds_number', 'bonds'),
        ('bond_types_len', 'bond_coeffs'),
        ('angles_number', 'angles'),
        ('angle_types_number', 'angle_coeff'),
        ('dihedrals_number', 'dihedrals'),
        ('dihedral_types_len', 'dihedral_coeffs'),
        ('impropers_number', 'impropers'),
        ('improper_types_len', 'improper_coeffs'),
    ]
    for item1, item2 in consistency:
        if item1 in topology and item2 in topology:
            if topology[item1] != len(topology[item2]):
                print(f'** NOT consistent {item1} != {item2} **')
            else:
                print(f'{item1} == {item2}')


def read_data_file(data_file):
    """Read the LAMMPS topology."""
    topology = {}

    current_section = None

    with open(data_file, 'r') as infile:
        for i, lines in enumerate(infile):
            if i == 0:  # skip first line
                continue
            strip = lines.strip()
            strip = strip.partition('#')[0]  # remove ccomments
            if not strip:  # skip empty lines
                continue
            if current_section is None:
                look_for_topology_info(strip, topology)
                look_for_box_info(strip, topology)
            # Check if we are to read for a specific section/block:
            section = look_for_section(strip)
            if section is not None:
                # We are to start reading for a new section:
                current_section = section.lower().replace(' ', '_')
                if current_section not in topology:
                    topology[current_section] = []
                continue
            if current_section:
                split = strip.split()
                fmt = FORMATS.get(current_section)
                if fmt is None:
                    fmt = [int] + [float] * len(split[1:])
                formatted = []
                for j, fmti in zip(split, fmt):
                    try:
                        formatted.append(fmti(j))
                    except ValueError:
                        formatted.append(float('nan'))
                topology[current_section].append(formatted)

    return topology


def guess_atom_names(topology):
    """Guess atom names from masses."""
    if 'masses' not in topology:
        return None
    atom_names = {}
    for atom_idx, mass in topology['masses']:
        diff = float('inf')
        for atom_name, massi in PERIODIC_TABLE.items():
            new_diff = abs(massi - mass)
            if new_diff < diff:
                diff = new_diff
                atom_names[atom_idx] = atom_name
    return atom_names


def print_molecule_info(molecules):
    """Print basic information about the molecules."""
    if molecules:
        print(f'Molecules: {len(molecules)}')
        for key in sorted(molecules.keys()):
            atoms = molecules[key]['atoms']
            charge = molecules[key]['charge']
            print(f'\tMolecule {key}:')
            print(f'\t\tAtoms: {len(atoms)}')
            print(f'\t\tCharge: {sum(charge)}')


def main(data_file):
    """Get the topology and create a .gro-file."""
    topology = read_data_file(data_file)
    check_topology_consistency(topology)
    # Extract info about molecules:
    molecules = get_molecules(topology)
    topology['molecules'] = molecules
    print_molecule_info(molecules)
    # Write structure to a gro file:
    atom_names = guess_atom_names(topology)
    # atom_names = {1: 'C', 2: 'H'}
    write_gro_file('test.gro', topology, atom_names=atom_names)


if __name__ == '__main__':
    main(sys.argv[1])
