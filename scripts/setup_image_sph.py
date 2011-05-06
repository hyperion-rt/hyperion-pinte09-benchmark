import os

import numpy as np

from hyperion.model import AnalyticalYSOModel
from hyperion.util.constants import rsun, pi, sigma, au, msun
from hyperion.dust import SphericalDust

from hyperion.util.functions import create_dir

prefix = 'sph_0.8.0'

if not os.path.exists(prefix):
    create_dir(prefix)

create_dir('%s/models_images' % prefix)

for i, tau in enumerate([1e6]):

    m = AnalyticalYSOModel('%s/models_images/tau%3.0e' % (prefix,tau))

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

    theta = np.array([69.5, 87.1])
    phi = np.array([45., 45.])

    image = m.add_peeled_images()
    image.set_viewing_angles(theta, phi)
    image.set_image_size(251, 251)
    image.set_image_limits(-450.*au, 450.*au, -450.*au, 450.*au)
    image.set_aperture_range(1, 450.*au, 450.*au)
    image.set_wavelength_range(1, 0.9, 1.1)

    m.set_raytracing(True)

    m.set_n_initial_iterations(0)

    # theta resolution matters for the edge-on viewing angles. Doing it with
    # the new auto (twice as much resolution at the midplane as at the poles)
    # gives a much beter agreement

    m.set_spherical_polar_grid_auto(399,299,1,rmax=500.*au)

    m.specific_energy = '%s/models/tau%3.0e.rtout' % (prefix,tau)

    m.set_monochromatic(True, wavelengths=np.array([1.]))

    m.set_mrw(True, gamma=2.)
    m.set_pda(True)
    m.set_n_photons(imaging_sources=1000000000, imaging_dust=20000000000, raytracing_sources=10000000, raytracing_dust=10000000, stats=100000)
    m.set_max_interactions(10000)

    m.write()
