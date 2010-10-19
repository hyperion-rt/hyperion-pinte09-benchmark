import sys, os

prefix, output = sys.argv[1:3]

if not os.path.exists(prefix):
    raise Exception("No such directory: %s" % prefix)

if not os.path.exists(output):
    raise Exception("No such directory: %s" % output)

import h5py
from hyperionrt.util.constants import au
from hyperionrt.util.integrate import interp1d_log10
import numpy as np
from scipy.interpolate import RectBivariateSpline

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as mpl

# Set matplotlib preferences
mpl.rc('axes', titlesize='x-small')
mpl.rc('axes', labelsize='x-small')
mpl.rc('xtick', labelsize='xx-small')
mpl.rc('ytick', labelsize='xx-small')
mpl.rc('xtick.major', size=2)
mpl.rc('ytick.major', size=2)
mpl.rc('xtick.minor', size=1)
mpl.rc('ytick.minor', size=1)
mpl.rc('font', family='serif')
mpl.rc('axes', linewidth=0.5)
mpl.rc('patch', linewidth=0.5)
mpl.rc('text', usetex=True)
mpl.rc('ps', fonttype=42)

# Plotting settings

xmargin = 0.05
ymargin = 0.05

dx = 0.5 - 2 * xmargin
dy = (0.5 - 2 * ymargin) / 3.

fig = mpl.figure(figsize=(6.5, 5.0))
artists = []

for tau in ['1e3','1e6']:

    # Get Hyperion results
    f = h5py.File(prefix + '/models/tau%3.0e.rtout' % float(tau))
    temperature = f['Iteration 00010']['temperature'][0,0,:,:]

    f = h5py.File(prefix + '/models/tau%3.0e.rtin' % float(tau))

    if 'w' in f['Grid/Geometry/Walls 1'].dtype.names:

        grid_type = 'cylindrical'

        w = f['Grid/Geometry/Walls 1']['w']
        z = f['Grid/Geometry/Walls 2']['z']

        w = np.array(0.5*(w[1:] + w[:-1])).astype(np.float64)
        z = np.array(0.5*(z[1:] + z[:-1])).astype(np.float64)

    else:
        grid_type = 'spherical'

        r = f['Grid/Geometry/Walls 1']['r']
        t = f['Grid/Geometry/Walls 2']['t']

        r = np.array(0.5*(r[1:] + r[:-1])).astype(np.float64)
        t = np.array(0.5*(t[1:] + t[:-1])).astype(np.float64)

    temperature = np.array(temperature).astype(np.float64).transpose()

    # Transform radius
    # r_midplane_hyperion = (r[1:]-0.1*au)

    if grid_type == 'cylindrical':
        temperature_interp = RectBivariateSpline(w, z, temperature, kx=1, ky=1)
    else:
        temperature_interp = RectBivariateSpline(r, t, temperature, kx=1, ky=1)

    rcyl1 = np.ones(100) * 0.2*au
    zcyl1 = np.linspace(0., 0.1*au, 100)

    z_vertical1_hyperion = zcyl1 / au

    if grid_type == 'cylindrical':
        temp_vertical1_hyperion = temperature_interp.ev(rcyl1, zcyl1)
    else:
        rsph1 = np.sqrt(rcyl1*rcyl1 + zcyl1*zcyl1)
        tsph1 = np.arctan2(rcyl1, zcyl1)
        temp_vertical1_hyperion = temperature_interp.ev(rsph1, tsph1)

    temp_vertical1_hyperion_i = interp1d_log10(z_vertical1_hyperion, temp_vertical1_hyperion, bounds_error=False)

    rcyl2 = np.ones(100) * 200.*au
    zcyl2 = np.linspace(0., 150*au, 100)

    z_vertical2_hyperion = zcyl2 / au

    if grid_type == 'cylindrical':
        temp_vertical2_hyperion = temperature_interp.ev(rcyl2, zcyl2)
    else:
        rsph2 = np.sqrt(rcyl2*rcyl2 + zcyl2*zcyl2)
        tsph2 = np.arctan2(rcyl2, zcyl2)
        temp_vertical2_hyperion = temperature_interp.ev(rsph2, tsph2)

    temp_vertical2_hyperion_i = interp1d_log10(z_vertical2_hyperion, temp_vertical2_hyperion, bounds_error=False)

    if grid_type == 'cylindrical':
        rcyl3 = w[1:]
        zcyl3 = np.zeros(rcyl3.shape)
        r_midplane_hyperion = rcyl3 / au
        temp_midplane_hyperion = temperature_interp.ev(rcyl3, zcyl3)
    else:
        rsph3 = r[1:]
        tsph3 = np.ones(rsph3.shape) * np.radians(90.)
        r_midplane_hyperion = rsph3 / au
        temp_midplane_hyperion = temperature_interp.ev(rsph3, tsph3)

    temp_midplane_hyperion_i = interp1d_log10(r_midplane_hyperion, temp_midplane_hyperion, bounds_error=False)

    # Get MCFOST results

    data = np.loadtxt('benchmark/mcfost/tau=%s_aniso/T/Radial_temp_tau=%s.txt' % (tau, tau), dtype=[('r', float), ('temperature', float)])
    r_midplane_mcfost = data['r']
    temp_midplane_mcfost = data['temperature']
    temp_midplane_mcfost_i = interp1d_log10(r_midplane_mcfost, temp_midplane_mcfost, bounds_error=False)

    data = np.loadtxt('benchmark/mcfost/tau=%s_aniso/T/Vertical_temp_R=0.2AU_tau=%s.txt' % (tau, tau), dtype=[('z', float), ('temperature', float)])
    z_vertical1_mcfost = data['z']
    temp_vertical1_mcfost = data['temperature']
    temp_vertical1_mcfost_i = interp1d_log10(z_vertical1_mcfost, temp_vertical1_mcfost, bounds_error=False)

    data = np.loadtxt('benchmark/mcfost/tau=%s_aniso/T/Vertical_temp_R=200AU_tau=%s.txt' % (tau, tau), dtype=[('z', float), ('temperature', float)])
    z_vertical2_mcfost = data['z']
    temp_vertical2_mcfost = data['temperature']
    temp_vertical2_mcfost_i = interp1d_log10(z_vertical2_mcfost, temp_vertical2_mcfost, bounds_error=False)

    # Get TORUS results

    data = np.loadtxt('benchmark/torus/tau=%s_aniso/T/tau=%s_aniso_radial.dat' % (tau, tau), dtype=[('r', float), ('temperature', float)])
    r_midplane_torus = data['r']
    temp_midplane_torus = data['temperature']
    temp_midplane_torus_i = interp1d_log10(r_midplane_torus, temp_midplane_torus, bounds_error=False)

    data = np.loadtxt('benchmark/torus/tau=%s_aniso/T/tau=%s_aniso_vert1.dat' % (tau, tau), dtype=[('z', float), ('temperature', float)])
    z_vertical1_torus = data['z']
    temp_vertical1_torus = data['temperature']
    temp_vertical1_torus_i = interp1d_log10(z_vertical1_torus, temp_vertical1_torus, bounds_error=False)

    data = np.loadtxt('benchmark/torus/tau=%s_aniso/T/tau=%s_aniso_vert2.dat' % (tau, tau), dtype=[('z', float), ('temperature', float)])
    z_vertical2_torus = data['z']
    temp_vertical2_torus = data['temperature']
    temp_vertical2_torus_i = interp1d_log10(z_vertical2_torus, temp_vertical2_torus, bounds_error=False)

    # Get MCMax results

    data = np.loadtxt('benchmark/mcmax/tau=%s_aniso/T/midplane_temp_tau%s.dat' % (tau, tau), dtype=[('r', float), ('temperature', float)])
    r_midplane_mcmax = data['r']
    temp_midplane_mcmax = data['temperature']
    temp_midplane_mcmax_i = interp1d_log10(r_midplane_mcmax, temp_midplane_mcmax, bounds_error=False)

    data = np.loadtxt('benchmark/mcmax/tau=%s_aniso/T/vertical_temp_0.2AU_tau%s.dat' % (tau, tau), dtype=[('z', float), ('temperature', float)])
    z_vertical1_mcmax = data['z'][::-1]
    temp_vertical1_mcmax = data['temperature'][::-1]
    temp_vertical1_mcmax_i = interp1d_log10(z_vertical1_mcmax, temp_vertical1_mcmax, bounds_error=False)

    data = np.loadtxt('benchmark/mcmax/tau=%s_aniso/T/vertical_temp_200AU_tau%s.dat' % (tau, tau), dtype=[('z', float), ('temperature', float)])
    z_vertical2_mcmax = data['z'][::-1]
    temp_vertical2_mcmax = data['temperature'][::-1]
    temp_vertical2_mcmax_i = interp1d_log10(z_vertical2_mcmax, temp_vertical2_mcmax, bounds_error=False)

    print temp_vertical1_mcfost_i(0.01)
    print temp_vertical1_mcmax_i(0.01)
    print temp_vertical1_torus_i(0.01)

    # Find average midplane temperature

    r_midplane = np.array(list(set(r_midplane_mcfost.tolist() + r_midplane_torus.tolist() + r_midplane_mcmax.tolist())))
    r_midplane = np.unique(r_midplane)
    r_midplane.sort()

    temp_midplane = np.zeros(r_midplane.shape)

    use_hyperion = ~np.isnan(temp_midplane_hyperion_i(r_midplane))

    use_mcfost = ~np.isnan(temp_midplane_mcfost_i(r_midplane))
    temp_midplane[use_mcfost] += temp_midplane_mcfost_i(r_midplane)[use_mcfost]

    use_torus = ~np.isnan(temp_midplane_torus_i(r_midplane))
    temp_midplane[use_torus] += temp_midplane_torus_i(r_midplane)[use_torus]

    use_mcmax = ~np.isnan(temp_midplane_mcmax_i(r_midplane))
    temp_midplane[use_mcmax] += temp_midplane_mcmax_i(r_midplane)[use_mcmax]

    temp_midplane /= (use_mcfost.astype(int) + use_torus.astype(int) + use_mcmax.astype(int))

    # RADIAL ABSOLUTE

    if tau is '1e3':
        xmin = xmargin
    else:
        xmin = 0.5 + xmargin

    ymin = 0.5 + ymargin + dy

    ax = fig.add_axes([xmin, ymin, dx, dy*2])

    ax.loglog(r_midplane_mcfost-0.1, temp_midplane_mcfost, color='gray', lw=0.5)
    ax.loglog(r_midplane_torus-0.1, temp_midplane_torus, color='gray', lw=0.5)
    ax.loglog(r_midplane_mcmax-0.1, temp_midplane_mcmax, color='gray', lw=0.5)
    ax.loglog(r_midplane_hyperion-0.1, temp_midplane_hyperion, color='black', lw=1.0)

    ax.set_xlim(1.e-6, 400.)
    ax.xaxis.set_major_formatter(mpl.NullFormatter())
    ax.set_ylim(5.,2000.)
    ax.yaxis.set_major_formatter(mpl.FixedFormatter(['1','10','100','1000']))

    artist = ax.text(-0.13, 0.5, r'Temperature (K)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
    artists.append(artist)

    ax.text(0.975, 0.95,r'$\tau_{I}=10^%s$, midplane' % tau[2],ha='right',va='top',transform=ax.transAxes, size='small')

    # RADIAL DIFFERENCE

    ymin = 0.5 + ymargin

    ax = fig.add_axes([xmin, ymin, dx, dy])

    ax.plot(r_midplane[use_mcfost]-0.1, 100.*(temp_midplane_mcfost_i(r_midplane)[use_mcfost] - temp_midplane[use_mcfost]) / temp_midplane[use_mcfost], color='gray')
    ax.plot(r_midplane[use_torus]-0.1, 100.*(temp_midplane_torus_i(r_midplane)[use_torus] - temp_midplane[use_torus]) / temp_midplane[use_torus], color='gray')
    ax.plot(r_midplane[use_mcmax]-0.1, 100.*(temp_midplane_mcmax_i(r_midplane)[use_mcmax] - temp_midplane[use_mcmax]) / temp_midplane[use_mcmax], color='gray')
    ax.plot(r_midplane[use_hyperion]-0.1, 100.*(temp_midplane_hyperion_i(r_midplane)[use_hyperion] - temp_midplane[use_hyperion])/ temp_midplane[use_hyperion], color='black')

    ax.set_xscale('log')
    ax.set_xlim(1.e-6, 400.)
    ax.set_xlabel('Radius (AU) - 0.1AU')

    if tau is '1e3':
        ax.set_ylim(-5.,5.)
    elif tau is '1e6':
        ax.set_ylim(-15.,15.)
    ax.axhline(0., lw=0.5, ls='dashed', color='black')
    ax.yaxis.set_ticks([-10., 0., 10.])
    artist = ax.text(-0.13, 0.5, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
    artists.append(artist)

    if tau is '1e6':

        # Find average vertical1 temperature

        z_vertical1 = np.array(list(set(z_vertical1_mcfost.tolist() + z_vertical1_torus.tolist() + z_vertical1_mcmax.tolist())))
        z_vertical1 = np.unique(z_vertical1)
        z_vertical1.sort()

        temp_vertical1 = np.zeros(z_vertical1.shape)

        use_hyperion = ~np.isnan(temp_vertical1_hyperion_i(z_vertical1))

        use_mcfost = ~np.isnan(temp_vertical1_mcfost_i(z_vertical1))
        temp_vertical1[use_mcfost] += temp_vertical1_mcfost_i(z_vertical1)[use_mcfost]

        use_torus = ~np.isnan(temp_vertical1_torus_i(z_vertical1))
        temp_vertical1[use_torus] += temp_vertical1_torus_i(z_vertical1)[use_torus]

        use_mcmax = ~np.isnan(temp_vertical1_mcmax_i(z_vertical1))
        temp_vertical1[use_mcmax] += temp_vertical1_mcmax_i(z_vertical1)[use_mcmax]

        temp_vertical1 /= (use_mcfost.astype(int) + use_torus.astype(int) + use_mcmax.astype(int))

        # VERTICAL ABSOLUTE 0.2AU

        xmin = xmargin

        ymin = ymargin + dy

        ax = fig.add_axes([xmin, ymin, dx, dy*2])

        ax.plot(z_vertical1_mcfost, temp_vertical1_mcfost, color='gray', lw=0.5)
        ax.plot(z_vertical1_torus, temp_vertical1_torus, color='gray', lw=0.5)
        ax.plot(z_vertical1_mcmax, temp_vertical1_mcmax, color='gray', lw=0.5)
        ax.plot(z_vertical1_hyperion, temp_vertical1_hyperion, color='black', lw=1.0)

        ax.set_xlim(0.,0.065)
        ax.xaxis.set_major_formatter(mpl.NullFormatter())
        ax.set_ylim(200., 800.)
        # ax.yaxis.set_major_formatter(mpl.FixedFormatter(['1','10','100','1000']))

        artist = ax.text(-0.13, 0.5, r'Temperature (K)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
        artists.append(artist)

        ax.text(0.025, 0.95,r'$\tau_{I}=10^%s$, $r=0.2$ AU' % tau[2],ha='left',va='top',transform=ax.transAxes, size='small')

        # VERTICAL DIFFERENCE 0.2AU

        ymin = ymargin

        ax = fig.add_axes([xmin, ymin, dx, dy])

        ax.plot(z_vertical1[use_mcfost], 100.*(temp_vertical1_mcfost_i(z_vertical1)[use_mcfost] - temp_vertical1[use_mcfost]) / temp_vertical1[use_mcfost], color='gray')
        ax.plot(z_vertical1[use_torus], 100.*(temp_vertical1_torus_i(z_vertical1)[use_torus] - temp_vertical1[use_torus]) / temp_vertical1[use_torus], color='gray')
        ax.plot(z_vertical1[use_mcmax], 100.*(temp_vertical1_mcmax_i(z_vertical1)[use_mcmax] - temp_vertical1[use_mcmax]) / temp_vertical1[use_mcmax], color='gray')
        ax.plot(z_vertical1[use_hyperion], 100.*(temp_vertical1_hyperion_i(z_vertical1)[use_hyperion] - temp_vertical1[use_hyperion])/ temp_vertical1[use_hyperion], color='black')

        ax.set_xlim(0.,0.065)
        ax.set_xlabel('z (AU)')

        ax.set_ylim(-17.,17.)
        ax.axhline(0., lw=0.5, ls='dashed', color='black')
        ax.yaxis.set_ticks([-5., 0., 5.])
        artist = ax.text(-0.13, 0.5, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
        artists.append(artist)

        # Find average vertical2 temperature

        z_vertical2 = np.array(list(set(z_vertical2_mcfost.tolist() + z_vertical2_torus.tolist() + z_vertical2_mcmax.tolist())))
        z_vertical2 = np.unique(z_vertical2)
        z_vertical2.sort()

        temp_vertical2 = np.zeros(z_vertical2.shape)

        use_hyperion = ~np.isnan(temp_vertical2_hyperion_i(z_vertical2))

        use_mcfost = ~np.isnan(temp_vertical2_mcfost_i(z_vertical2))
        temp_vertical2[use_mcfost] += temp_vertical2_mcfost_i(z_vertical2)[use_mcfost]

        use_torus = ~np.isnan(temp_vertical2_torus_i(z_vertical2))
        temp_vertical2[use_torus] += temp_vertical2_torus_i(z_vertical2)[use_torus]

        use_mcmax = ~np.isnan(temp_vertical2_mcmax_i(z_vertical2))
        temp_vertical2[use_mcmax] += temp_vertical2_mcmax_i(z_vertical2)[use_mcmax]

        temp_vertical2 /= (use_mcfost.astype(int) + use_torus.astype(int) + use_mcmax.astype(int))

        # VERTICAL ABSOLUTE 0.2AU

        xmin = 0.5+xmargin

        ymin = ymargin + dy

        ax = fig.add_axes([xmin, ymin, dx, dy*2])

        ax.plot(z_vertical2_mcfost, temp_vertical2_mcfost, color='gray', lw=0.5)
        ax.plot(z_vertical2_torus, temp_vertical2_torus, color='gray', lw=0.5)
        ax.plot(z_vertical2_mcmax, temp_vertical2_mcmax, color='gray', lw=0.5)
        ax.plot(z_vertical2_hyperion, temp_vertical2_hyperion, color='black', lw=1.0)

        ax.set_xlim(0.,150.)
        ax.xaxis.set_major_formatter(mpl.NullFormatter())
        ax.set_ylim(15., 50.)
        # ax.yaxis.set_major_formatter(mpl.FixedFormatter(['1','10','100','1000']))

        artist = ax.text(-0.13, 0.5, r'Temperature (K)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
        artists.append(artist)

        ax.text(0.025, 0.95,r'$\tau_{I}=10^%s$, $r=200$ AU' % tau[2],ha='left',va='top',transform=ax.transAxes, size='small')

        # VERTICAL DIFFERENCE 0.2AU

        ymin = ymargin

        ax = fig.add_axes([xmin, ymin, dx, dy])

        ax.plot(z_vertical2[use_mcfost], 100.*(temp_vertical2_mcfost_i(z_vertical2)[use_mcfost] - temp_vertical2[use_mcfost]) / temp_vertical2[use_mcfost], color='gray')
        ax.plot(z_vertical2[use_torus], 100.*(temp_vertical2_torus_i(z_vertical2)[use_torus] - temp_vertical2[use_torus]) / temp_vertical2[use_torus], color='gray')
        ax.plot(z_vertical2[use_mcmax], 100.*(temp_vertical2_mcmax_i(z_vertical2)[use_mcmax] - temp_vertical2[use_mcmax]) / temp_vertical2[use_mcmax], color='gray')
        ax.plot(z_vertical2[use_hyperion], 100.*(temp_vertical2_hyperion_i(z_vertical2)[use_hyperion] - temp_vertical2[use_hyperion])/ temp_vertical2[use_hyperion], color='black')

        ax.set_xlim(0.,150.)
        ax.set_xlabel('z (AU)')

        ax.set_ylim(-17.,17.)
        ax.axhline(0., lw=0.5, ls='dashed', color='black')
        ax.yaxis.set_ticks([-5., 0., 5.])
        artist = ax.text(-0.13, 0.5, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
        artists.append(artist)

fig.savefig('%s/temperatures.eps' % output, bbox_inches='tight', bbox_extra_artists=artists)
fig.savefig('%s/temperatures.png' % output, bbox_inches='tight', bbox_extra_artists=artists)
