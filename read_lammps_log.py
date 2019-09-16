"""Read data from a LAMMPS log file."""
from math import ceil
import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec


plt.style.use('seaborn-talk')


def read_lammps_log(logfile):
    """Read data from a LAMMPS log file."""
    keys = None
    data = []
    read = False
    with open(logfile) as infile:
        for lines in infile:
            if lines.startswith('Step'):
                if data:
                    yield keys, data
                keys = [i.lower() for i in lines.strip().split()]
                data = []
                read = True
                continue
            if read:
                if lines.startswith('Loop time'):
                    if data:
                        yield keys, data
                        data = []
                        keys = None
                        read = False
                else:
                    new_data = [float(i) for i in lines.strip().split()]
                    if data:
                        if len(new_data) != len(data[-1]):
                            print('Inconsistent length of data --- skipping.')
                        else:
                            data.append(new_data)
                    else:
                        data.append(new_data)
    if data:
        yield keys, data


def plot_all_items(data):
    """Plot all items in the given dictionary."""
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
        axi.plot(xpos, val, lw=2, alpha=0.8)
        axi.axhline(y=np.average(val), lw=2, ls='--', color='#262626',
                    alpha=0.8)
        axi.set_xlabel('Step no.')
        axi.set_ylabel(key)
    fig.tight_layout()


def plot_selected_items(xdata, data, selection, add_average=False):
    """Plot some selected data in the same plot."""
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for key in selection:
        line, = ax1.plot(xdata, data[key], lw=2, alpha=0.8, label=key)
        if add_average:
            ax1.axhline(y=np.average(data[key]), lw=2, ls=':',
                        color=line.get_color(), alpha=0.8)
    ax1.legend(loc='upper left')
    fig.tight_layout()


def main(logfile):
    """Read a LAMMPS log and plot some selected data."""
    for keys, data in read_lammps_log(logfile):
        print('Set found')
        print('Keys:')
        for i in keys:
            print('- {}'.format(i))
        print('Length: {}'.format(len(data)))
        data_matrix = np.array(data)
        data_dict = {}
        for i, key in enumerate(keys):
            data_dict[key] = data_matrix[:, i]
        plot_all_items(data_dict)
        plot_selected_items(
            data_dict['step'],
            data_dict,
            ['c_hot_temp', 'c_cold_temp'],
            add_average=True
        )
        data_dict['sum_rescale'] = (
            data_dict['f_hot_rescale'] + data_dict['f_cold_rescale']
        )
        plot_selected_items(
            data_dict['step'],
            data_dict,
            ['f_cold_rescale', 'f_hot_rescale', 'sum_rescale'],
            add_average=True
        )
    plt.show()


if __name__ == '__main__':
    main(sys.argv[1])
