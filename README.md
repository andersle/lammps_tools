# lammps_tools
A collection of tools for interacting with LAMMPS

## install-lammps.sh

A script for installing LAMMPS.

Usage:

```bash
sh install-lammps.sh
```

## read_lammps_log.py

A script for plotting variables from the thermo output of LAMMPS.

Usage:

```bash
python read_lammps_log.py log.lammps
```

### Notes

* The script makes certain assumptions on what variables to plot.

## read_lammps_data.py

A script for reading topology information from LAMMPS data files.

Usage:

```bash
python read_lammps_data.py system.data
```

### Notes

* This script will attempt to write a GROMACS .gro file with the
  system coordinates.
* It will probably be more useful to modify the script to suit
  your needs, e.g. if you want to investigate bonds, angles etc.


## average_lammps_profile.py

A script for averaging profiles created by LAMMPS.

Usage:

```bash
python average_lammps_profile.py -f temp1.txt -p
```

### Notes

* The profiles are assumed to be written by LAMMPS using a command like:
  ```
  fix out_temp1 all ave/chunk 5 1000 5000 cc1 temp file temp1.txt
  ```

## average_lammps_rdf.py

A script for averaging RDFs created by LAMMPS.

Usage:

```bash
python average_lammps_profile.py -f rdf-X-Y.txt -p
```
### Notes

* The RDFs are assumed to be written by LAMMPS using a command like:
  ```
  fix fix_rdf_X_Y all ave/time 100 1 100 c_rdf_X_Y[*] file rdf-X-Y.txt mode vector
  ```

## skip_lammpstrj.py

A script for reducing the size of .lammpstrj files. It will write a new file with every N'th frame.

Usage:

```bash
python skip_lammpstrj.py infile.lammpstrj 100
```

This will produce a new file ``infile-skip-100.lammpstrj`` with every 100th frame from ``infile.lammpstrj``.
