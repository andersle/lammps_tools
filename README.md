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


## average_lammps_profile.py

A script for averaging profiles created by LAMMPS.

Usage:

```bash
python average_lammps_profile.py -f temp1.txt -p
```

### Notes

* The script makes certain assumptions on what variables to plot.

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
