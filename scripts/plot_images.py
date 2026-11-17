import sys, os

prefix, output = sys.argv[1:3]

if not os.path.exists(prefix):
    raise Exception("No such directory: %s" % prefix)

if not os.path.exists(output):
    raise Exception("No such directory: %s" % output)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as mpl

from hyperion.model import ModelOutput
from hyperion.util.constants import pc

import numpy as np

from astropy.io import fits as pyfits

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

m = ModelOutput('%s/models_images/tau%3.0e.rtout' % (prefix, 1e6))

xmargin = 0.01
ymargin = 0.01

dx = 0.25 - 2 * xmargin
dy = 0.25 - 2 * ymargin

vmin = 1.e-23
vmax = 2.e-18
cmap = mpl.cm.gist_heat
cmapd = mpl.cm.RdBu

rang = {}
rang[0] = {}
rang[0][0] = (3e-21, 3e-20)
rang[0][1] = (3e-21, 1e-19)
rang[0][2] = (1e-22, 1e-17)
rang[2] = {}
rang[2][0] = (4e-20, 6e-19)
rang[2][1] = (2e-20, 7e-19)
rang[2][2] = (5e-23, 1e-18)


for stokes in ['I','linpol']:
    
    fig = mpl.figure(figsize=(6.5, 6.5))
    
    mcfost = {}
    mcmax = {}
    torus = {}
    pinball = {}
    average = {}
    
    if stokes == 'I':
        mcfost[0] = pyfits.getdata('benchmark/mcfost/tau=1e6_aniso/images/intensity_map_inc070.fits.gz')
        mcfost[2] = pyfits.getdata('benchmark/mcfost/tau=1e6_aniso/images/intensity_map_inc087.fits.gz')
        mcmax[0] = pyfits.getdata('benchmark/mcmax/tau=1e6_aniso/images/ImageF_i69.5_l00001.00_fov00900.0.fits')
        mcmax[2] = pyfits.getdata('benchmark/mcmax/tau=1e6_aniso/images/ImageF_i87.1_l00001.00_fov00900.0.fits')
        torus[0] = pyfits.getdata('benchmark/torus/tau=1e6_aniso/images/tau=1e6_aniso_inc070_natural_image001.fits')
        torus[2] = pyfits.getdata('benchmark/torus/tau=1e6_aniso/images/tau=1e6_aniso_inc087_natural_image001.fits')
        pinball[0] = pyfits.getdata('benchmark/pinball/images/0.35/escape-xy-0-mean.fits')[14:-14,14:-14] / 67802792611.0
        pinball[2] = pyfits.getdata('benchmark/pinball/images/0.05/escape-xy-0-mean.fits')[14:-14,14:-14] / 67802792611.0
#        average[0] = (mcfost[0] + mcmax[0] + torus[0] + pinball[0]) / 4.
#        average[2] = (mcfost[2] + mcmax[2] + torus[2] + pinball[2]) / 4.
        average[0] = (mcfost[0] + mcmax[0] + pinball[0]) / 3.
        average[2] = (mcfost[2] + mcmax[2] + pinball[2]) / 3.
    else:
        mcfost[0] = pyfits.getdata('benchmark/mcfost/tau=1e6_aniso/pola/linear_polarization_map_inc070.fits.gz')
        mcfost[2] = pyfits.getdata('benchmark/mcfost/tau=1e6_aniso/pola/linear_polarization_map_inc087.fits.gz')
        mcmax[0] = pyfits.getdata('benchmark/mcmax/tau=1e6_aniso/pola/ImageP_i69.5_l00001.00_fov00900.0.fits')
        mcmax[2] = pyfits.getdata('benchmark/mcmax/tau=1e6_aniso/pola/ImageP_i87.1_l00001.00_fov00900.0.fits')
        torus[0] = pyfits.getdata('benchmark/torus/tau=1e6_aniso/pola/tau=1e6_aniso_inc070_natural_pol001.fits')
        torus[2] = pyfits.getdata('benchmark/torus/tau=1e6_aniso/pola/tau=1e6_aniso_inc087_natural_pol001.fits')
        pinball[0] = pyfits.getdata('benchmark/pinball/pola/pola_inc70.fits')
        pinball[2] = pyfits.getdata('benchmark/pinball/pola/pola_inc87.fits')
        average[0] = (mcfost[0] + mcmax[0] + pinball[0]) / 3.
        average[2] = (mcfost[2] + mcmax[2] + pinball[2]) / 3.
             
    for incl in range(4):

        x0 = 0.
        y0 = 0.75 - incl / 4.

        if incl % 2 == 0:

            # Retrieve image
            if stokes == 'I':
                distance=140.*pc
            else:
                distance=None

            wav, image = m.get_image(distance=distance, inclination=incl//2, stokes=stokes)
            
            image = image.swapaxes(0,2)
            image = image.swapaxes(1,2)

            if incl in [0,1]:
                v = 126-30
                h1 = 126+50
                h2 = 126-50
            else:
                v = 126-50
                h1 = 126+30
                h2 = 126-30
                
            if stokes is 'I':
                # Conversion to W/m^2
                image *= 1.e-3
                image_display = (np.clip((image[0,:,:] - vmin) / (vmax - vmin),0,1))**0.25
            else:
                image_display = image[0,:,:]
                image_display[np.isnan(image_display)] = 0.

            # Show image in left panels
            ax = fig.add_axes([x0+xmargin-0.05, y0+ymargin, dx, dy])
            ax.imshow(image_display, vmin=0, vmax=1, origin='lower', cmap=cmap)
            ax.axhline(h1, color='white')
            ax.text(225,h1+10,'1', color='white', size='x-small')
            ax.axhline(h2, color='white')
            ax.text(225,h2+10,'2', color='white', size='x-small')
            ax.axvline(v, color='white')
            ax.text(v+10, 225,'3', color='white', size='x-small')
            ax.xaxis.set_major_formatter(mpl.NullFormatter())
            ax.yaxis.set_major_formatter(mpl.NullFormatter())

            x = np.arange(251) - 125
        
            cuth = {}
            cuth[0] = np.mean(image[0,h1-5:h1+6,:], axis=0)
            cuth[1] = np.mean(image[0,h2-5:h2+6,:], axis=0)
            cuth[2] = np.mean(image[0,:,v-5:v+6], axis=1)
        
            cut_mcfost = {}
            cut_mcfost[0] = np.mean(mcfost[incl][h1-5:h1+6,:], axis=0)
            cut_mcfost[1] = np.mean(mcfost[incl][h2-5:h2+6,:], axis=0)
            cut_mcfost[2] = np.mean(mcfost[incl][:,v-5:v+6], axis=1)
               
            cut_mcmax = {}
            cut_mcmax[0] = np.mean(mcmax[incl][h1-5:h1+6,:], axis=0)
            cut_mcmax[1] = np.mean(mcmax[incl][h2-5:h2+6,:], axis=0)
            cut_mcmax[2] = np.mean(mcmax[incl][:,v-5:v+6], axis=1)
               
            cut_torus = {}
            cut_torus[0] = np.mean(torus[incl][h1-5:h1+6,:], axis=0)
            cut_torus[1] = np.mean(torus[incl][h2-5:h2+6,:], axis=0)
            cut_torus[2] = np.mean(torus[incl][:,v-5:v+6], axis=1)
               
            cut_pinball = {}
            cut_pinball[0] = np.mean(pinball[incl][h1-5:h1+6,:], axis=0)
            cut_pinball[1] = np.mean(pinball[incl][h2-5:h2+6,:], axis=0)
            cut_pinball[2] = np.mean(pinball[incl][:,v-5:v+6], axis=1)
        
            cut_average = {}
            cut_average[0] = np.mean(average[incl][h1-5:h1+6,:], axis=0)
            cut_average[1] = np.mean(average[incl][h2-5:h2+6,:], axis=0)
            cut_average[2] = np.mean(average[incl][:,v-5:v+6], axis=1)
        
            for cut in range(3):
            
                x0 = 0.25 + 0.25 * cut
                ax = fig.add_axes([x0+xmargin, y0+ymargin, dx, dy])
                if stokes is 'I':
                    fact = 10.**(np.log10(rang[incl][cut][1] / rang[incl][cut][0]) / 30.)
                    if incl == 0 or (incl==2 and cut==2):
                        ax.axhline(1.e-20, color='gray', lw=0.5, label='100')
                        ax.text(0, 1.e-20 / fact, r'$10^{-20}$', va='top', size='xx-small', ha='center', color='gray')
                    elif incl == 2:
                        ax.axhline(1.e-19, color='gray', lw=0.5, label='100')
                        ax.text(0, 1.e-19 / fact, r'$10^{-19}$', va='top', size='xx-small', ha='center', color='gray')
                ax.plot(x, cut_mcfost[cut], color='gray', lw=0.5)
                ax.plot(x, cut_mcmax[cut], color='gray', lw=0.5)
                if stokes is 'I':
                    ax.plot(x, cut_torus[cut], color='gray', lw=0.5)
                ax.plot(x, cut_pinball[cut], color='gray', lw=0.5)
                ax.plot(x, cuth[cut], color='black', lw=1.0)
                ax.set_xlim(-125.,125.)
                if stokes is 'I':
                    ax.set_yscale('log')                
                    ax.set_ylim(rang[incl][cut][0],rang[incl][cut][1])
                else:
                    ax.set_ylim(0.,1.)
                    
                if stokes is 'I':    
                    if cut == 0:
                        ax.set_ylabel(r'Flux (ergs/cm$^2$/s)')
                else:
                    if cut == 0:
                        ax.set_ylabel('Polarization')
                        
                ax.xaxis.set_major_formatter(mpl.NullFormatter())
                if incl % 2 != 0 or cut != 0 or stokes is "I":
                    ax.yaxis.set_major_formatter(mpl.NullFormatter())

        else:
        
            for cut in range(3):
            
                x0 = 0.25 + 0.25 * cut
                ax = fig.add_axes([x0+xmargin, y0+ymargin, dx, dy])
                if stokes is 'I':
                    ax.plot(x, (cut_mcfost[cut]-cut_average[cut])/cut_average[cut]*100., color='gray', lw=0.5)
                    ax.plot(x, (cut_mcmax[cut]-cut_average[cut])/cut_average[cut]*100., color='gray', lw=0.5)
                    ax.plot(x, (cut_torus[cut]-cut_average[cut])/cut_average[cut]*100., color='gray', lw=0.5)
                    ax.plot(x, (cut_pinball[cut]-cut_average[cut])/cut_average[cut]*100., color='gray', lw=0.5)
                    ax.plot(x, (cuth[cut]-cut_average[cut])/cut_average[cut]*100., color='black', lw=1.0)
                else:
                    ax.plot(x, cut_mcfost[cut]-cut_average[cut], color='gray', lw=0.5)
                    ax.plot(x, cut_mcmax[cut]-cut_average[cut], color='gray', lw=0.5)
                    # ax.plot(x, cut_torus[cut]-cut_average[cut], color='gray', lw=0.5)
                    ax.plot(x, cut_pinball[cut]-cut_average[cut], color='gray', lw=0.5)
                    ax.plot(x, cuth[cut]-cut_average[cut], color='black', lw=1.0)
                    
                ax.set_xlim(-125.,125.)
                if stokes is 'I':
                    ax.set_ylim(-20.,20.)
                else:
                    ax.set_ylim(-0.15,0.15)
                    
                if cut == 3 and incl == 3:
                    ax.set_xlabel('Pixel')
                
                if stokes is 'I':    
                    if cut == 0:
                        ax.set_ylabel('Difference (\%)')
                else:
                    if cut == 0:
                        ax.set_ylabel('Difference')
                
                if incl != 3:
                    ax.xaxis.set_major_formatter(mpl.NullFormatter())
                if cut > 0:
                    ax.yaxis.set_major_formatter(mpl.NullFormatter())

    fig.savefig('%s/images_%s.eps' % (output, stokes), bbox_inches='tight')
    fig.savefig('%s/images_%s.png' % (output, stokes), bbox_inches='tight')

