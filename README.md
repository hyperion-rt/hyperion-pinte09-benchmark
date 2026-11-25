# Hyperion Pinte et al. (2009) benchmark

This repository contains the scripts used to run the
[Pinte et al. (2009)](https://doi.org/10.1051/0004-6361/200811555) disk
benchmark with the [Hyperion](http://www.hyperion-rt.org) radiative transfer
code, and to compare the resulting temperatures, SEDs and images to the
results from the other codes in `benchmark/`.

The benchmark defines the SEDs at specific wavelengths, so the SEDs are
computed in Hyperion's monochromatic mode (plotted in `seds.png`). The SEDs of
each model are also computed a second time in the normal (non-monochromatic)
mode, re-using the temperatures, with the SEDs binned in wavelength and
interpolated to the benchmark wavelengths (plotted in `seds_binned.png`), to
check that this mode also agrees with the other codes. The images are only
computed in monochromatic mode.

## Requirements

- The Hyperion Python package and the MPI versions of the Fortran binaries
  (`hyperion_sph_mpi` and `hyperion_cyl_mpi`), with the binaries on the `PATH`
- `mpirun`
- [Snakemake](https://snakemake.github.io) 8 or later
- SciPy
- A LaTeX installation, which Matplotlib uses to render the text in the plots

## Running the benchmark

The workflow is defined in `Snakefile` and configured in `config.yaml`. Before
running, set `version` in `config.yaml` to a label for the version of Hyperion
being tested, since this is used to name the output directory.

To check that everything runs, use the fast profile, which takes around 40
seconds per model on 8 cores:

    snakemake --config profile=fast

All the output is written to a directory named after the version, with the
plots for each grid geometry in e.g. `v1.0.0b2/sph/plots`. The fast results are
written to a separate directory ending in `_fast` (for example
`v1.0.0b2_fast`). They are noisy and the temperatures are not converged, so
they are only useful for testing the workflow and not for judging the
agreement with the other codes.

To run the full benchmark:

    snakemake

This is very expensive: there are ten models (four optical depths and one
image model for each of the spherical and cylindrical polar grids), as well
as a run to compute the binned SEDs for each of the eight models, and with
v1.0.0b2 the full profile would take of order tens of thousands of CPU hours in
total, almost all of it in the dust photons for the SEDs. The numbers of
photons in this profile are the ones used for the published results, which
were computed with an earlier and much cheaper (but noisier) algorithm for
the dust photons, so they are far more than are needed now.

The reduced profile uses ten times fewer photons for the temperature
calculation and many fewer photons for the SEDs and images:

    snakemake --config profile=reduced

With v1.0.0b2 this takes about 540 CPU hours in total (about 17 hours on 32
cores): about 310 for the models, 30 for the images and 200 for the binned
SEDs. The SEDs are noisier at mid-infrared wavelengths for the most edge-on
viewing angle of the most optically thick model than with the full profile.
The images use enough photons from the star that the noise in the
polarization maps is comparable to the differences between the other codes.
The results are written to a separate directory ending in `_reduced`.

A subset of the results can be requested by giving the files to produce, for
example:

    snakemake v1.0.0b2/sph/plots/temperatures.png

Any files to produce have to be given before `--config` on the command line.

By default each model is run with as many MPI processes as there are cores on
the machine. To use fewer, either limit the cores available to Snakemake with
e.g. `--cores 8`, or set `mpi_processes` to a number in `config.yaml`.

The default Snakemake options in `profiles/default/config.yaml` run one model
at a time and only re-run a model if its output is missing or older than its
input, so to deliberately re-run a model either delete its output or use
`--forcerun`.

## Running in a container

The `Containerfile` can be used to build an image with Hyperion and all the
other requirements, for example with [Podman](https://podman.io). The version
of Hyperion to build is set with `HYPERION_REF`, which can be a tag, a branch
or a commit, and defaults to `main`:

    podman build --build-arg HYPERION_REF=v1.0.0b2 -t hyperion-benchmark:v1.0.0b2 .

If `HYPERION_REF` is a branch, building again re-uses the previous build
rather than picking up new commits, so in that case either add `--no-cache` or
give the commit instead. The version that was built is recorded in
`/etc/hyperion-version` inside the image.

The benchmark is not included in the image, so the repository has to be
mounted when running the workflow, and the output is then written to the
repository as usual:

    podman run --rm -it --shm-size=2g -v $PWD:/work:Z hyperion-benchmark:v1.0.0b2 \
        snakemake --config profile=fast

The `--shm-size` option is needed because the default amount of shared memory
in a container is too small to start a large number of MPI processes. Leaving
out the `snakemake` command gives a shell inside the container instead.

## Remaking plots

Since editing a script does not cause anything to be re-run, a plot has to be
explicitly remade after changing one of the plotting scripts. None of the
following re-run the models, provided that the model output is already there.

To remake one kind of plot for both grid geometries, force the rule that makes
it, which is one of `plot_seds`, `plot_seds_binned`, `plot_temperatures` or
`plot_images`:

    snakemake --forcerun plot_seds

To remake the plots for a single grid geometry, give one of the files and use
`--force`:

    snakemake v1.0.0b2/sph/plots/seds.png --force

Alternatively, delete the plots to remake and run `snakemake` again, which
only produces the files that are missing.

For the fast results, add `--config profile=fast` at the end of the command
and use the paths in the `_fast` directory. To check which steps would be run
without running anything, add `-n` to any of these commands.
