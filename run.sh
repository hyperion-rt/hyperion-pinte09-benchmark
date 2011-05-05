#!/bin/bash -x

VERSION="0.7.8"

# SPHERICAL

# First the two that matter for the temperature plots
mpirun -n 8 hyperion_sph_mpi sph_$VERSION/models/tau1e+03.rt{in,out}
mpirun -n 8 hyperion_sph_mpi sph_$VERSION/models/tau1e+06.rt{in,out}

# Then the two others
mpirun -n 8 hyperion_sph_mpi sph_$VERSION/models/tau1e+04.rt{in,out}
mpirun -n 8 hyperion_sph_mpi sph_$VERSION/models/tau1e+05.rt{in,out}
 
# CYLINDRICAL

# First the two that matter for the temperature plots
mpirun -n 8 hyperion_cyl_mpi cyl_$VERSION/models/tau1e+03.rt{in,out}
mpirun -n 8 hyperion_cyl_mpi cyl_$VERSION/models/tau1e+06.rt{in,out}

# Then the two others
mpirun -n 8 hyperion_cyl_mpi cyl_$VERSION/models/tau1e+04.rt{in,out}
mpirun -n 8 hyperion_cyl_mpi cyl_$VERSION/models/tau1e+05.rt{in,out}


