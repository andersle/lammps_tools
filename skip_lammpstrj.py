#!/usr/bin/env python
"""Write a reduced lammpstrj file by skipping frames."""
import pathlib
import sys
import re
import io
import mmap
from tqdm import tqdm


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


def count_frames(lmp):
    """Count the number of frames in a lammpstrj file."""
    pattern = re.compile(b'ITEM: TIMESTEP')
    with io.open(lmp, 'r', encoding='utf-8') as infile:
        match = pattern.finditer(
            mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)
        )
        return sum(1 for _ in match)
    return 0


def main(infile, skip=10):
    """Write a reduced lammpstrj file by skipping frames."""
    print('Skip: {}'.format(skip))
    print('Infile: {}'.format(infile))
    infile_path = pathlib.Path(infile).resolve()
    outfile = '{}-skip-{}.lammpstrj'.format(
        str(pathlib.Path(infile).stem), skip
    )
    print('Outfile: {}'.format(outfile))

    outfile_path = infile_path.parent.joinpath(outfile)

    print('Getting number of frames in original file...')
    frames_tot = count_frames(infile_path)
    print('Frames in original file: {}'.format(frames_tot))
    if frames_tot < 1:
        print('No frames found, exiting...')
        return

    frames = 0
    frames_read = 0
    with tqdm(total=frames_tot) as pbar:
        with open(outfile_path, 'w') as output:
            for i, frame in enumerate(read_lammpstrj(infile_path)):
                frames_read += 1
                pbar.update(1)
                if i % skip == 0:
                    frames += 1
                    output.write(''.join(frame))
        print('Frames read: {}'.format(frames_read))
        print('Frames written to new file: {}'.format(frames))
    return


if __name__ == '__main__':
    try:
        main(sys.argv[1], skip=int(sys.argv[2]))
    except IndexError:
        main(sys.argv[1])
