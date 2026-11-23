import numpy as np

from hyperion.model import Model
from hyperion.util.constants import rsun, pi, sigma, au, msun
from hyperion.dust import SphericalDust

# The settings that differ between the full and fast runs come from the
# profile selected in config.yaml, and are passed in by the Snakefile.

settings = snakemake.params.settings

m = Model()

# Star:
#
# T_star = 4,000K
# R_star = 2 * R_sun

star = m.add_spherical_source()
star.radius = 2. * rsun
star.temperature = 4000.
star.luminosity = 4. * pi * (2. * rsun) ** 2. * sigma * 4000. ** 4.

m.use_geometry(snakemake.input.model)
m.use_quantities(snakemake.input.model)

# SEDs/Images:
#
# cos(i) = 0.05 to 0.95 in steps of 0.1
# Images computed at 1 micron
# 251 pixels/900 AU across, at 140 pc

# theta = np.degrees(np.arccos(np.linspace(0.05,0.95,10)))
# phi = np.ones(10) * 30

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

m.set_n_initial_iterations(0)

# theta resolution matters for the edge-on viewing angles. Doing it with
# the new auto (twice as much resolution at the midplane as at the poles)
# gives a much beter agreement

# Limits on the optical depths for peeled photons and for emitting dust
# photons, which make the imaging much faster in these very optically thick
# models (see config.yaml for details). These options are not available in
# older versions of Hyperion, in which case they are not used.
limits = snakemake.params.optical_depth_limits
mono_kwargs = {}
if hasattr(m, 'set_max_peeloff_optical_depth'):
    m.set_max_peeloff_optical_depth(limits['max_peeloff_optical_depth'])
if hasattr(m, 'set_compute_escape_column_density'):
    m.set_compute_escape_column_density(True, rays_per_cell=limits['escape_rays_per_cell'])
    mono_kwargs['emission_max_escape_optical_depth'] = limits['emission_max_escape_optical_depth']

m.set_monochromatic(True, wavelengths=np.array([1.]), **mono_kwargs)

m.set_mrw(True, gamma=2.)
m.set_pda(True)
m.set_n_photons(**settings['n_photons'])
m.set_max_interactions(10000)

m.write(snakemake.output[0])
