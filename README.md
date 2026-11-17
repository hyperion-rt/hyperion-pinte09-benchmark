# Hyperion Pinte et al. (2009) benchmark

This repository contains the scripts used to run the
[Pinte et al. (2009)](https://doi.org/10.1051/0004-6361/200811555) disk
benchmark with the [Hyperion](http://www.hyperion-rt.org) radiative transfer
code, and to compare the resulting temperatures, SEDs and images to the
results from the other codes in `benchmark/`.

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

To check that everything runs, use the fast profile, which takes around a
minute per model on 8 cores:

    snakemake --config profile=fast

All the output is written to a directory named after the version, with the
plots for each grid geometry in e.g. `0.9.12/sph/plots`. The fast results are
written to a separate directory ending in `_fast` (for example
`0.9.12_fast`). They are noisy and the temperatures are not converged, so
they are only useful for testing the workflow and not for judging the
agreement with the other codes.

To run the full benchmark:

    snakemake

This is very expensive: the original runs took of order 350 CPU hours per
model, and there are ten models (four optical depths and one image model for
each of the spherical and cylindrical polar grids).

A subset of the results can be requested by giving the files to produce, for
example:

    snakemake 0.9.12/sph/plots/temperatures.png

Any files to produce have to be given before `--config` on the command line.

By default each model is run with as many MPI processes as there are cores on
the machine. To use fewer, either limit the cores available to Snakemake with
e.g. `--cores 8`, or set `mpi_processes` to a number in `config.yaml`.

The default Snakemake options in `profiles/default/config.yaml` run one model
at a time and only re-run a model if its output is missing or older than its
input, so to deliberately re-run a model either delete its output or use
`--forcerun`.
