"""Average profiles from LAMMPS."""
import argparse
from math import ceil
import pathlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.gridspec import GridSpec


plt.style.use('seaborn-talk')


def read_lammps_profile(filename):
    """Read the profiles from chunked LAMMPS output."""
    with open(filename, 'r') as infile:
        cols = 0  # number of columns
        lines_to_read = 0  # number of lines in a set
        data = []
        keys = []
        for lines in infile:
            if lines.find('# Chunk ') != -1:
                # read shape of data
                linesplit = lines.strip().split()
                cols = len(linesplit) - 1
                keys = [key.lower() for key in linesplit[1:]]
                continue
            if cols > 0:
                linesplit = lines.strip().split()
                if lines_to_read > 0:
                    if len(linesplit) == cols:
                        data.append([float(i) for i in linesplit])
                        lines_to_read -= 1
                else:
                    if data:
                        yield keys, step, data
                        data = []
                    step, lines_to_read = [int(i) for i in linesplit[:2]]
        if data:
            yield keys, step, data


def update_variance(xdata, length, mean, var_m2):
    """Update estimate of mean and variance with new observations."""
    length = length + 1.0
    delta = xdata - mean
    mean = mean + delta / length
    var_m2 = var_m2 + delta * (xdata - mean)
    if length < 2:
        variance = float('inf')
    else:
        variance = var_m2 / (length - 1.0)
    return length, mean, var_m2, variance


def average_profiles(infile):
    """Read the given input file and return averaged profiles."""
    raw_data_matrix = []
    raw_data = {}
    # Variables for averaging:
    average_data = {}
    n_data = {}
    m2_data = {}
    var_data = {}
    for keys, _, data in read_lammps_profile(infile):
        raw_data_matrix.append(data)
        new_data = np.array(data)
        for i, key in enumerate(keys):
            column = new_data[:, i]
            if key not in average_data:
                average_data[key] = np.zeros_like(column)
                m2_data[key] = np.zeros_like(column)
                n_data[key] = 0.0
                var_data[key] = np.full_like(column, float('inf'))
            new_n, new_mean, new_m2, new_var = update_variance(
                column,
                n_data[key],
                average_data[key],
                m2_data[key],
            )
            n_data[key] = new_n
            average_data[key] = new_mean
            m2_data[key] = new_m2
            var_data[key] = new_var
            if key not in raw_data:
                raw_data[key] = []
            raw_data[key].append(column)
    return raw_data, raw_data_matrix, average_data, var_data


def plot_all_items(data, error):
    """Plot all items in a dict."""
    fig = plt.figure()
    if len(data) < 3:
        ncol = 1
    else:
        ncol = 2
    nrow = ceil(len(data) / ncol)
    grid = GridSpec(nrow, ncol)
    for i, (key, val) in enumerate(data.items()):
        row, col = divmod(i, ncol)
        axi = fig.add_subplot(grid[row, col])
        xpos = np.arange(len(val))
        std = np.sqrt(error[key])
        axi.fill_between(xpos, val - std, val + std, alpha=0.5)
        axi.plot(xpos, val, lw=2)
        axi.set_xlabel('Bin no.')
        axi.set_ylabel(key)
    fig.tight_layout()


def plot_xy_data(xdata, ydata, yerror=None, xlabel='x', ylabel='y'):
    """Plot xy data."""
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    if yerror is not None:
        ax1.fill_between(xdata, ydata - yerror, ydata + yerror, alpha=0.5)
        ax1.plot(xdata, ydata - yerror, ls=':', alpha=0.5, color='#262626')
        ax1.plot(xdata, ydata + yerror, ls=':', alpha=0.5, color='#262626')
    line, = ax1.plot(xdata, ydata, lw=2)
    ax1.scatter(xdata, ydata, marker='o', alpha=0.5, color=line.get_color())
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    fig.tight_layout()


def plot_all_sets(raw_data, key, color_map_name='viridis'):
    """Plot all sets for a given variable."""
    data = raw_data[key]
    cmap = get_cmap(name=color_map_name)
    colors = cmap(np.linspace(0, 1, len(data)))
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    xpos = None
    for i, datai in enumerate(data):
        if xpos is None:
            xpos = np.arange(len(datai))
        ax1.plot(xpos, datai, color=colors[i], alpha=0.5)
    ax1.set_xlabel('Bin no.')
    ax1.set_ylabel(key)
    fig.tight_layout()


def write_output(filename, keys, data):
    """Store the data in a new file."""
    header = ' '.join(['#'] + keys)
    cols = len(keys)
    rows = len(data[keys[0]])
    data_matrix = np.zeros((rows, cols))
    for i, key in enumerate(keys):
        data_matrix[:, i] = data[key]
    print('Writing file "{}"'.format(filename))
    np.savetxt(filename, data_matrix, header=header)


def write_output_error(filename, keys, data, error):
    """Store the data in a new file."""
    header = ['#']
    for key in keys:
        header.append(key)
        header.append('std_{}'.format(key))
    cols = len(keys) * 2
    rows = len(data[keys[0]])
    data_matrix = np.zeros((rows, cols))
    for i, key in enumerate(keys):
        data_matrix[:, 2 * i] = data[key]
        data_matrix[:, 2 * i + 1] = np.sqrt(error[key])
    print('Writing file "{}"'.format(filename))
    np.savetxt(filename, data_matrix, header=' '.join(header))


def main(infile, make_plot, split=False):
    """Read the input file and average the profiles within it."""
    print('Reading file "{}"'.format(infile))
    raw_data, raw_matrix, average_data, var_data = average_profiles(infile)
    print('Data sets: {}'.format(len(raw_matrix)))
    print('Variables in sets:')
    for i in raw_data:
        print('- "{}"'.format(i))
    if make_plot:
        print('Plotting all averaged profiles.')
        plot_all_items(average_data, var_data)
        plot_all_sets(raw_data, 'ncount')
        plot_all_sets(raw_data, 'v_kintemp')
        xkey = 'coord1'
        for ykey in ('ncount', 'v_kintemp'):
            plot_xy_data(
                average_data[xkey],
                average_data[ykey],
                yerror=np.sqrt(var_data[ykey]),
                xlabel=xkey,
                ylabel=ykey,
            )
    write_output(
        'averaged-{}.txt'.format(pathlib.Path(infile).stem),
        [i for i in average_data],
        average_data
    )
    write_output_error(
        'averaged-error-{}.txt'.format(pathlib.Path(infile).stem),
        [i for i in average_data],
        average_data,
        var_data,
    )
    if split:
        for i in average_data:
            write_output_error(
                'averaged-{}-{}.txt'.format(
                    i, pathlib.Path(infile).stem
                ),
                [i],
                average_data,
                var_data,
            )


def create_parser():
    """Create a parser."""
    parser = argparse.ArgumentParser(description='Average profile from lammps')
    parser.add_argument(
        '-f',
        '--file',
        help='File to average',
        required=True,
        default='x-temp.txt'
    )
    parser.add_argument(
        '-s',
        '--split',
        help='Write a new file for each variable',
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '-p',
        '--plot',
        help='Write a new file for each variable',
        required=False,
        action='store_true'
    )
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    main(ARGS.file, ARGS.plot, split=ARGS.split)
    if ARGS.plot:
        plt.show()
