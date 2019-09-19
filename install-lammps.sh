tarfile=lammps-stable.tar.gz
wget http://lammps.sandia.gov/tars/$tarfile

tmp_dir=lammps-source
mkdir -p $tmp_dir
tar xvf $tarfile --directory $tmp_dir

cd $tmp_dir
lmp_dir=$(find . -maxdepth 1 -type d -name 'lammps-*' -print -quit)
version=$(echo $lmp_dir | cut -d '-' -f 2)
echo $version

target_dir=~/opt/lammps/$version
target_exe=lammps-$version

cd lammps-$version
mkdir -p build
rm -rf build/*
cd build

# Building with GNU Compilers:
#C_COMPILER=gcc
#CXX_COMPILER=g++
#F_COMPILER=gfortran
# Building with Intel Compilers:
#C_COMPILER=icc
#CXX_COMPILER=icpc
#F_COMPILER=ifort
# Building with LLVM/Clang Compilers:
C_COMPILER=clang
CXX_COMPILER=clang++
F_COMPILER=flang

cmake -D BUILD_MPI=on -D CMAKE_INSTALL_PREFIX=$target_dir -D CMAKE_C_COMPILER=$C_COMPILER -D CMAKE_CXX_COMPILER=$CXX_COMPILER -D CMAKE_Fortran_COMPILER=$F_COMPILER -D PKG_KSPACE=YES -D PKG_MANYBODY=YES -D PKG_MOLECULE=YES -D PKG_RIGID=YES -D PKG_USER-TALLY=YES ../cmake

make -j4

cp lmp ~/bin/lmp-$version
