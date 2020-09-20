"""Read a LAMMPS trajectory created from a dump."""
import sys
import numpy as np


# Format for GROMACS gro files:
_GRO_FMT = '{0:5d}{1:5s}{2:5s}{3:5d}{4:8.3f}{5:8.3f}{6:8.3f}'
_GRO_BOX_FMT = '{:15.9f}'


def write_gro_file(outputfile, data, atom_names=None, mode='w'):
    """Create a gro file from the topology."""
    step = data.get('timestep', 0)
    number = data.get('number of atoms', None)

    atoms = data.get('atoms', {})

    if number is None:
        for _, val in atoms.items():
            number = len(val)
            break

    if atom_names is None:
        atom_names = atoms.get('element', [])

    try:
        idx = np.argsort(atoms['id'])
    except KeyError:
        idx = range(len(number))

    with open(outputfile, mode) as output:
        output.write(f'Converted from LAMMPS data, step {step}\n')
        output.write(f'{number}\n')

        for i in idx:
            mol_idx = 1
            if 'mol' in atoms:
                mol_idx = atoms['mol'][i]
            atom_type = 1
            if 'type' in atoms:
                atom_type = atoms['type'][i]
            atom_name = 'X'
            if atom_names:
                atom_name = atom_names[i]
            else:
                atom_name = f'X{atom_type}'
            buff = _GRO_FMT.format(
                mol_idx,
                'MOL',
                atom_name,
                atom_type,
                atoms['x'][i] * 0.1,
                atoms['y'][i] * 0.1,
                atoms['z'][i] * 0.1,
            )
            output.write(f'{buff}\n')
        box = data.get('box', None)
        if box is not None:
            blx = 0.1 * (box['xhi'] - box['xlo'])
            bly = 0.1 * (box['yhi'] - box['ylo'])
            blz = 0.1 * (box['zhi'] - box['zlo'])
            box_length = [blx, bly, blz]
            if 'xy' in box:
                box_length.extend(
                    [
                        0.0, 0.0, box['xy'] * 0.1, 0.0,
                        box['xz'] * 0.1, box['yz'] * 0.1
                    ]
                )
            box_str = ' '.join([_GRO_BOX_FMT.format(i) for i in box_length])
            output.write(f'{box_str}\n')


def guess_string_format(string):
    """Guess if a string represents an integer, a float or a string."""
    try:
        _ = int(string)
        return int
    except ValueError:
        try:
            _ = float(string)
            return float
        except ValueError:
            return str


def read_lammpstrj(lmp):
    """Iterate frames in a lammpstrj file."""
    raw = []
    with open(lmp, 'r') as infile:
        for lines in infile:
            if lines.startswith('ITEM: TIMESTEP'):
                if raw:
                    yield raw
                raw = []
            raw.append(lines)
    if raw:
        yield raw


def read_box_line(line, box, dim):
    """Read box info from a line."""
    raw = line.strip().split()
    box[f'{dim}lo'] = float(raw[0])
    box[f'{dim}hi'] = float(raw[1])
    if len(raw) > 2:
        if dim == 'x':
            box['xy'] = float(raw[2])
        elif dim == 'y':
            box['xz'] = float(raw[2])
        else:
            box['yz'] = float(raw[2])
    return box


def read_for_box(box, line):
    """Read box information from a line."""
    if 'xlo' in box or 'xhi' in box:
        if 'ylo' in box or 'yhi' in box:
            read_box_line(line, box, 'z')
        else:
            read_box_line(line, box, 'y')
    else:
        read_box_line(line, box, 'x')


def read_atom_data(atom_format, line):
    """Format the data information."""
    if atom_format is None:
        _format = [guess_string_format(i.strip()) for i in line.split()]
    else:
        _format = atom_format
    formatted = []
    for i, (val, fmti) in enumerate(zip(line.split(), _format)):
        istrip = val.strip()
        try:
            formatted.append(fmti(istrip))
        except ValueError:
            fmt = guess_string_format(istrip)
            _format[i] = fmt
            formatted.append(fmt(istrip))
    return formatted, _format


def frame_to_dict(frame):
    """Convert a raw data frame to a dictionary."""
    item = None
    atom_format = None
    data = {}
    for lines in frame:
        if lines.startswith('ITEM:'):
            item = lines.strip().split('ITEM:')[1].lower().strip()
            item_split = item.split()
            if item_split[0] == 'box':
                item = 'box'
                data[item] = {'bounds': [str(i) for i in item_split[2:]]}
            elif item_split[0] == 'atoms':
                item = 'atoms'
                data[item] = {i: [] for i in item_split[1:]}
            else:
                data[item] = []
            continue
        if item is not None:
            if item in ('timestep', 'number of atoms'):
                data[item] = int(lines.strip())
            elif item in ('box',):
                read_for_box(data['box'], lines)
            elif item in ('atoms',):
                formatted, atom_format = read_atom_data(atom_format, lines)
                for key, val in zip(data['atoms'].keys(), formatted):
                    data['atoms'][key].append(val)
            else:
                data[item].append(lines.strip())
    for key, val in data['atoms'].items():
        data['atoms'][key] = np.array(val)
        if len(data['atoms'][key]) != data['number of atoms']:
            print(f'Inconsistent data length for {key}')
    return data


def main(infile):
    """Write a reduced lammpstrj file by skipping frames."""
    for i, frame in enumerate(read_lammpstrj(infile)):
        data = frame_to_dict(frame)
        print(i, data['timestep'], data['number of atoms'])


if __name__ == '__main__':
    main(sys.argv[1])
