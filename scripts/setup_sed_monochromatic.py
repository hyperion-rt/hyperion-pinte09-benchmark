# Set up a run that computes the SEDs for one of the Pinte et al. (2009)
# benchmark models at the benchmark wavelengths in monochromatic mode,
# re-using the temperatures from the model. The settings that differ between
# profiles come from config.yaml and are passed in by the Snakefile.

from common import WAVELENGTHS, model_from_temperatures, add_sed, set_optical_depth_limits, write

settings = snakemake.params.settings

m = model_from_temperatures(snakemake.input.model)

add_sed(m)

m.set_raytracing(True)

monochromatic_kwargs = set_optical_depth_limits(m, snakemake.params.optical_depth_limits)
m.set_monochromatic(True, wavelengths=WAVELENGTHS, **monochromatic_kwargs)

m.set_mrw(True, gamma=2.)
m.set_pda(True)

m.set_n_photons(**settings['n_photons'])

m.set_max_interactions(10000000)

write(m, snakemake.output[0])
