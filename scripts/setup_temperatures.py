# Set up one of the Pinte et al. (2009) benchmark models, which computes the
# temperatures. The SEDs and images are computed by separate runs that re-use
# these temperatures. The optical depth and grid geometry come from the
# Snakemake wildcards, and the settings that differ between profiles come
# from config.yaml and are passed in by the Snakefile.

from hyperion.model import AnalyticalYSOModel
from hyperion.util.constants import au, msun
from hyperion.dust import SphericalDust

from common import DUST_FILE, set_star, write

tau = float(snakemake.wildcards.tau)
geometry = snakemake.wildcards.geometry
settings = snakemake.params.settings

m = AnalyticalYSOModel()

set_star(m.star)

# Disk:
#
# Sigma(r) = Sigma_0 * (r/r_0)^-1.5
# h(r) = h_0 * (r/r_0)^1.125
# h_0 = 10 AU at 100AU
# r_in = 0.1AU, r_out = 400AU
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

disk.dust = SphericalDust(DUST_FILE)

m.set_n_initial_iterations(settings['n_initial_iterations'])
m.set_convergence(True, percentile=99., absolute=2., relative=1.02)

# theta resolution matters for the edge-on viewing angles. Doing it with
# the new auto (twice as much resolution at the midplane as at the poles)
# gives a much beter agreement

if geometry == 'sph':
    m.set_spherical_polar_grid_auto(*settings['grid'], 1, rmax=500. * au)
else:
    m.set_cylindrical_polar_grid_auto(*settings['grid'], 1)

m.set_mrw(True, gamma=2.)
m.set_pda(True)

# Only the temperatures are computed, so no photons are needed for imaging
m.set_n_photons(imaging=0, **settings['n_photons'])

m.set_max_interactions(10000000)

write(m, snakemake.output[0])
