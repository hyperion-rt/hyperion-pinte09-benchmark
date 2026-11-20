import numpy as np

from hyperion.model import AnalyticalYSOModel
from hyperion.util.constants import rsun, pi, sigma, au, msun
from hyperion.dust import SphericalDust

# The settings that differ between the full and fast runs come from the
# profile selected in config.yaml, and are passed in by the Snakefile.

tau = float(snakemake.wildcards.tau)
settings = snakemake.params.settings

m = AnalyticalYSOModel()

# Star:
#
# T_star = 4,000K
# R_star = 2 * R_sun

m.star.radius = 2. * rsun
m.star.temperature = 4000.
m.star.luminosity = 4. * pi * (2. * rsun) ** 2. * sigma * 4000. ** 4.

# Disk:
#
# Sigma(r) = Sigma_0 * (r/r_0)^-1.5
# h(r) = h_0 * (r/r_0)^1.125
# h_0 = 10 AU at 100AU
# r_in = 0.1AU, r_out = 400AU\
# Sharp vertical edges in cylindrical polar coordinates
# Disk mass (dust!) = 3e-8, 3e-7, 3e-6, 3e-5

disk = m.add_flared_disk()
disk.p = -1.5
disk.beta = 1.125
disk.mass = 3.e-8 * msun * tau / 1.e3
disk.rmin = 0.1 * au
disk.rmax = 400 * au
disk.h_0 = 10 * au
disk.r_0 = 100. * au

disk.cylindrical_inner_rim = True
disk.cylindrical_outer_rim = True

# Dust:
#
# Spherical grains, 1 micron, 3.5g/cm^3

disk.dust = SphericalDust('dust/pinte_dust.hdf5')

# SEDs/Images:
#
# cos(i) = 0.05 to 0.95 in steps of 0.1
# Images computed at 1 micron
# 251 pixels/900 AU across, at 140 pc

# theta = np.degrees(np.arccos(np.linspace(0.05,0.95,10)))
# phi = np.ones(10) * 30

theta = np.degrees(np.arccos(np.array([0.95, 0.25, 0.15, 0.05])))
phi = np.array([45., 45., 45., 45.])

image = m.add_peeled_images()
image.set_viewing_angles(theta, phi)
image.set_image_size(1, 1)
image.set_image_limits(-450. * au, 450. * au, -450. * au, 450. * au)
image.set_aperture_range(1, 450. * au, 450. * au)

# Record the flux from each origin (source or dust, emitted or scattered) as
# well as the uncertainties, so that the signal-to-noise of each component can
# be checked
image.set_track_origin('basic')
image.set_uncertainties(True)

m.set_raytracing(True)

m.set_n_initial_iterations(settings['n_initial_iterations'])
m.set_convergence(True, percentile=99., absolute=2., relative=1.02)

# theta resolution matters for the edge-on viewing angles. Doing it with
# the new auto (twice as much resolution at the midplane as at the poles)
# gives a much beter agreement

m.set_spherical_polar_grid_auto(*settings['grid'], 1, rmax=500. * au)

wavelengths = np.loadtxt('benchmark/data/wavelength_points.txt')
m.set_monochromatic(True, wavelengths=wavelengths)

m.set_mrw(True, gamma=2.)
m.set_pda(True)

m.set_n_photons(**settings['n_photons'])

m.set_max_interactions(10000000)

# Stop integrating the optical depth for peeled photons beyond tau=100, which
# makes the imaging much faster in these very optically thick models and only
# neglects contributions attenuated by more than exp(-100). This option is not
# available in older versions of Hyperion.
if hasattr(m, 'set_max_peeloff_optical_depth'):
    m.set_max_peeloff_optical_depth(100.)

m.write(snakemake.output[0])
