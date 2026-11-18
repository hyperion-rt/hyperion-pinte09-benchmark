# Image with Hyperion and everything else needed to run the benchmark. The
# benchmark repository itself is not included, and should be mounted when
# running a container - see the README for how to build and use this.

FROM docker.io/library/python:3.13-slim-bookworm

# Compilers, HDF5 and MPICH to build Hyperion, and the LaTeX packages that
# Matplotlib needs to render the text in the plots. These come first so that
# this slow layer is re-used when building for a different Hyperion version.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates git make gcc gfortran \
        libhdf5-dev hdf5-helpers libmpich-dev mpich \
        texlive-latex-extra texlive-fonts-recommended cm-super dvipng \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir scipy snakemake

# The version of Hyperion to build, which can be a tag, a branch or a commit.
# Note that if this is a branch, re-building the image will re-use the
# previous build rather than pick up new commits unless --no-cache is used.
ARG HYPERION_REF=main
ARG HYPERION_REPOSITORY=https://github.com/hyperion-rt/hyperion.git

# Build the Python package and the MPI versions of the Fortran binaries for
# the two kinds of grid used by the benchmark, and record what was built in
# /etc/hyperion-version
RUN git clone ${HYPERION_REPOSITORY} /opt/hyperion \
    && cd /opt/hyperion \
    && git checkout ${HYPERION_REF} \
    && git submodule update --init \
    && ./configure --prefix=/usr/local \
    && make sph_mpi cyl_mpi \
    && make install \
    && pip install --no-cache-dir . \
    && echo "ref: ${HYPERION_REF}" > /etc/hyperion-version \
    && echo "commit: $(git rev-parse HEAD)" >> /etc/hyperion-version \
    && echo "describe: $(git describe --tags --always)" >> /etc/hyperion-version \
    && make clean

WORKDIR /work

CMD ["bash"]
