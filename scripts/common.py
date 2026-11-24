"""
Settings and helpers shared by the scripts that set up the Hyperion models
for the Pinte et al. (2009) benchmark. Snakemake adds the directory of each
script to the module search path, so these can be imported directly.
"""

import numpy as np

from hyperion.model import Model
from hyperion.util.constants import rsun, pi, sigma, au

# Star:
#
# T_star = 4,000K
# R_star = 2 * R_sun

STAR_RADIUS = 2. * rsun
STAR_TEMPERATURE = 4000.
STAR_LUMINOSITY = 4. * pi * STAR_RADIUS ** 2. * sigma * STAR_TEMPERATURE ** 4.

# The wavelengths at which the benchmark SEDs are defined (evenly spaced in
# log(wavelength))

WAVELENGTHS = np.loadtxt('benchmark/data/wavelength_points.txt')

# SEDs:
#
# cos(i) = 0.95, 0.25, 0.15, 0.05, in a 900 AU aperture at 140 pc

SED_THETA = np.degrees(np.arccos(np.array([0.95, 0.25, 0.15, 0.05])))
SED_PHI = np.array([45., 45., 45., 45.])


def set_star(star):
    """
    Set the properties of the star on a source (or the star of an
    AnalyticalYSOModel).
    """
    star.radius = STAR_RADIUS
    star.temperature = STAR_TEMPERATURE
    star.luminosity = STAR_LUMINOSITY


def model_from_temperatures(filename):
    """
    Set up a model with the geometry, density and temperatures of an
    existing run, for computing SEDs or images without recomputing the
    temperatures.
    """
    m = Model()
    set_star(m.add_spherical_source())
    m.use_geometry(filename)
    m.use_quantities(filename)
    m.set_n_initial_iterations(0)
    return m


def add_sed(m):
    """
    Add the peeled SEDs for the benchmark viewing angles, recording the
    origin of the flux (source or dust, emitted or scattered) and the
    uncertainties so that the signal-to-noise of each component can be
    checked.
    """
    image = m.add_peeled_images()
    image.set_viewing_angles(SED_THETA, SED_PHI)
    image.set_image_size(1, 1)
    image.set_image_limits(-450. * au, 450. * au, -450. * au, 450. * au)
    image.set_aperture_range(1, 450. * au, 450. * au)
    image.set_track_origin('basic')
    image.set_uncertainties(True)
    return image


def set_binned_sed_wavelengths(image, n_per_step):
    """
    Bin the SED for non-monochromatic runs in bins evenly spaced in
    log(wavelength), with n_per_step bins per spacing of the benchmark
    wavelengths, and placed such that each group of n_per_step bins is
    centred on a benchmark wavelength.
    """
    step = np.log10(WAVELENGTHS[-1] / WAVELENGTHS[0]) / (len(WAVELENGTHS) - 1)
    image.set_wavelength_range(n_per_step * len(WAVELENGTHS),
                               WAVELENGTHS[0] / 10 ** (step / 2),
                               WAVELENGTHS[-1] * 10 ** (step / 2))


def set_optical_depth_limits(m, limits):
    """
    Set the limits on the optical depths for peeled photons and for
    emitting dust photons, which make the imaging much faster in these very
    optically thick models (see config.yaml for details). These options are
    not available in older versions of Hyperion, in which case they are not
    used. This returns the keyword arguments to pass to set_monochromatic,
    which only apply in monochromatic mode.
    """
    monochromatic_kwargs = {}
    if hasattr(m, 'set_max_peeloff_optical_depth'):
        m.set_max_peeloff_optical_depth(limits['max_peeloff_optical_depth'])
    if hasattr(m, 'set_compute_escape_column_density'):
        m.set_compute_escape_column_density(True, rays_per_cell=limits['escape_rays_per_cell'])
        monochromatic_kwargs['emission_max_escape_optical_depth'] = limits['emission_max_escape_optical_depth']
    return monochromatic_kwargs
