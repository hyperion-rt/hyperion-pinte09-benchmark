# Set up the image model for the Pinte et al. (2009) benchmark, which computes
# images at 1 micron (in monochromatic mode) re-using the temperatures from
# the most optically thick model. The settings that differ between profiles
# come from config.yaml and are passed in by the Snakefile.

import numpy as np

from hyperion.util.constants import au

from common import model_from_temperatures, set_optical_depth_limits

settings = snakemake.params.settings

m = model_from_temperatures(snakemake.input.model)

# Images:
#
# Images computed at 1 micron
# 251 pixels/900 AU across, at 140 pc

theta = np.array([69.5, 87.1])
phi = np.array([45., 45.])

image = m.add_peeled_images()
image.set_viewing_angles(theta, phi)
image.set_image_size(251, 251)
image.set_image_limits(-450.*au, 450.*au, -450.*au, 450.*au)
image.set_aperture_range(1, 450.*au, 450.*au)
image.set_wavelength_range(1, 0.9, 1.1)
image.set_stokes(True)

# Record the flux from each origin (source or dust, emitted or scattered) as
# well as the uncertainties, so that the signal-to-noise of each component can
# be checked
image.set_track_origin('basic')
image.set_uncertainties(True)

m.set_raytracing(True)

monochromatic_kwargs = set_optical_depth_limits(m, snakemake.params.optical_depth_limits)
m.set_monochromatic(True, wavelengths=np.array([1.]), **monochromatic_kwargs)

m.set_mrw(True, gamma=2.)
m.set_pda(True)
m.set_n_photons(**settings['n_photons'])
m.set_max_interactions(10000)

m.write(snakemake.output[0])
