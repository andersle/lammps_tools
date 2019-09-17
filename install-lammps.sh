wget http://lammps.sandia.gov/tars/lammps-stable.tar.gz
tarfile=lammps-stable.tar.gz
version=7Aug19
target_dir=~/opt/lammps/$version
target_exe=lammps-$version
tmp_dir=lammps-source-$version

mkdir $tmp_dir
tar xvf $tarfile --directory $tmp_dir
cd $tmp_dir
cd lammps-$version
mkdir build
cd build
rm -rf *

cmake -D BUILD_MPI=on -D CMAKE_INSTALL_PREFIX=$target_dir -D CMAKE_C_COMPILER=clang -D CMAKE_CXX_COMPILER=clang++ -D CMAKE_Fortran_COMPILER=flang -D PKG_KSPCACE=YES -D PKG_MANYBODY=YES -D PKG_MOLECULE=YES -D PKG_RIGID=YES -D PKG_USER-TALLY=YES ../cmake

make -j4

cp lmp ~/bin/lmp-$version
