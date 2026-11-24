# Set up a run that computes the SEDs for one of the Pinte et al. (2009)
# benchmark models in the normal (non-monochromatic) mode, re-using the
# temperatures from the model. The SEDs are binned in wavelength, with four
# bins per spacing of the benchmark wavelengths, and the plotting script
# interpolates them to the benchmark wavelengths. The settings that differ
# between profiles come from config.yaml and are passed in by the Snakefile.

from common import model_from_temperatures, add_sed, set_binned_sed_wavelengths, set_optical_depth_limits, write

settings = snakemake.params.settings

m = model_from_temperatures(snakemake.input.model)

image = add_sed(m)
set_binned_sed_wavelengths(image, 4)

m.set_raytracing(True)

# Only the limits for peeled photons apply in the normal mode
set_optical_depth_limits(m, snakemake.params.optical_depth_limits)

m.set_mrw(True, gamma=2.)
m.set_pda(True)

m.set_n_photons(**settings['n_photons'])

m.set_max_interactions(10000000)

write(m, snakemake.output[0])
