import sys, os

prefix, output = sys.argv[1:3]

if not os.path.exists(prefix):
    raise Exception("No such directory: %s" % prefix)

if not os.path.exists(output):
    raise Exception("No such directory: %s" % output)

import glob

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as mpl

from hyperion.model import ModelOutput
from hyperion.util.constants import pc, pi, c, rsun
from hyperion.util.functions import B_nu

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

xmargin = 0.005
ymargin = 0.005

dx = 0.5 - 2 * xmargin
dy = (0.5 - 2 * ymargin) / 8.

tau_string = ['1e3', '1e4', '1e5', '1e6']
viewing_angles = [18,76,81,87]
vf = {}
vf[18] = 18.2
vf[76] = 75.5
vf[81] = 81.4
vf[87] = 87.1

def get_sed(filename):
    sedfile = np.loadtxt(filename, dtype=[('wav', float), ('flux', float)], usecols=[0, 1])
    wav = sedfile['wav']
    sed = sedfile['flux']*1000.
    return wav, sed

fig = mpl.figure(figsize=(6.5,7.5))
artists = []

for i, tau in enumerate(tau_string):
    
    print(tau)

    if i in [0,2]:
        x0 = 0.
    else:
        x0 = 0.5

    if i in [2,3]:
        y0 = 0.
    else:
        y0 = 0.5

    xmin = x0 + xmargin
    ymin = y0 + ymargin + dy * 3.

    ax2 = fig.add_axes([xmin, ymin, dx, 4*dy])

    for j, view in enumerate(viewing_angles):

        xmin = x0 + xmargin
        ymin = y0 + ymargin + dy * (2-j)

        ax = fig.add_axes([xmin, ymin, dx, dy])

        # Get Hyperion SED
        m = ModelOutput('%s/models/tau%3.0e.rtout' % (prefix, float(tau)))
        wav_hyperion, sed_hyperion = m.get_sed(distance=140.*pc, inclination=j)
        sed_hyperion = sed_hyperion[0]

        # Get all other SEDs
        wav_mcfost, sed_mcfost = get_sed('benchmark/mcfost/tau=%s_aniso/SED/tau=%s_aniso_inc%03i.dat' % (tau, tau, view))
        wav_mcmax, sed_mcmax = get_sed('benchmark/mcmax/tau=%s_aniso/SED/SED%4.1f.dat' % (tau, vf[view]))
        wav_torus, sed_torus = get_sed('benchmark/torus/tau=%s_aniso/SED/tau=%s_aniso_inc%03i.dat' % (tau, tau, view))

        # Compute average SED
        wav_average = wav_mcfost
        # sed_average = sed_mcfost
        sed_average = (sed_mcfost + sed_torus + sed_mcmax) / 3.

        # Plot differences
        ax.plot(wav_average, (sed_mcfost-sed_average)/sed_average*100., color='gray', lw=0.5)
        ax.plot(wav_average, (sed_mcmax-sed_average)/sed_average*100., color='gray', lw=0.5)
        ax.plot(wav_average, (sed_torus-sed_average)/sed_average*100., color='gray', lw=0.5)
        ax.plot(wav_average, (sed_hyperion-sed_average)/sed_average*100., color='black', lw=1.0)

        # X-axis
        ax.set_xscale('log')
        ax.set_xlim(0.12, 2000.)

        if j == 3 and i in [2,3]:
            ax.xaxis.set_major_formatter(mpl.FixedFormatter(['0.1','1','10','100','1000','10000']))
            ax.set_xlabel(r'$\lambda$ [$\mu$m]')
        else:
            ax.xaxis.set_major_formatter(mpl.FixedFormatter([''] * 6))

        # Y-axis
        ax.set_ylim(-40., 40.)
        ax.yaxis.set_ticks([-20., 0., 20.])

        if i % 2 == 0:
            pass
        else:
            ax.yaxis.set_major_formatter(mpl.NullFormatter())

        if j == 1 and i%2 == 0:
            artist = ax.text(-0.15, 0.0, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
            artists.append(artist)

        # Plot SEDs
        ax2.scatter(wav_average, sed_average, color='gray', marker='o', lw=0, s=5, edgecolor='none')
        ax2.loglog(wav_average, sed_hyperion, color='black', lw=0.5)

    # Plot stellar photosphere
    nu_average = c/(wav_average*1.e-4)
    ax2.loglog(wav_average, pi*B_nu(nu_average, 4000.)*nu_average * (2*rsun)**2/(140*pc)**2, ls='dashed', lw=0.5, color='black')

    # X-axis
    ax2.set_xlim(0.12, 2000.)
    ax2.xaxis.set_major_formatter(mpl.NullFormatter())
    if i%2 == 0:
        artist = ax2.text(-0.15, 0.5, r'$\lambda F_\lambda$ [ergs/cm$^2$/s]', rotation='vertical', ha='center', va='center', transform=ax2.transAxes, size='x-small')
        artists.append(artist)

    # Y-axis
    ax2.set_ylim(1e-18, 1e-8)
    if i % 2 == 0:
        pass
    else:
        ax2.yaxis.set_major_formatter(mpl.NullFormatter())
    ax2.text(0.975, 0.95, r'$\tau_{I}=10^%i$' % (i+3), ha='right', va='top', transform = ax2.transAxes, size='small')

fig.savefig('%s/seds.pdf' % output, bbox_inches='tight', bbox_extra_artists=artists)
fig.savefig('%s/seds.png' % output, bbox_inches='tight', bbox_extra_artists=artists)

