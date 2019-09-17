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

cmake -D BUILD_MPI=on -D CMAKE_INSTALL_PREFIX=$target_dir -D CMAKE_C_COMPILER=clang -D CMAKE_CXX_COMPILER=clang++ -D CMAKE_Fortran_COMPILER=flang -D PKG_KSPCACE=YES -D PKG_MANYBODY=YES -D PKG_MOLECULE=YES -D PKG_RIGID=YES -D PKG_USER-TALLY=YES ../cmake

make -j4

cp lmp ~/bin/lmp-$version
