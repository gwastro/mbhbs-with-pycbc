import pandas as pd
import numpy as np
import subprocess
import os

import ldc.io.hdf5 as hdfio
from ldc.common import tools

from bbhx.utils.transform import SSB_to_LISA


sangria_fn = "../../../mbhb-unblinded.h5"
mbhb, units = hdfio.load_array(sangria_fn, name="sky/mbhb/cat")
pd.DataFrame(mbhb)
sigs = pd.DataFrame(mbhb).to_dict('records')

cwd = os.getcwd()


def spin_conv(mag, pol):
    return mag*np.cos(pol)

bbhx_sigs = {}

for i in range(6):
    wave = sigs[i]

    psi, incl = tools.aziPolAngleL2PsiIncl(wave["EclipticLatitude"],
                                       wave["EclipticLongitude"],
                                       wave['InitialPolarAngleL'],
                                       wave['InitialAzimuthalAngleL'])

    wave['approximant'] = 'BBHX_PhenomD'
    wave['mass1'] = wave.pop('Mass1')
    wave['mass2'] = wave.pop('Mass2')
    wave['spin1z'] = spin_conv(wave['Spin1'],wave['PolarAngleOfSpin1'])
    wave['spin2z'] = spin_conv(wave['Spin2'],wave['PolarAngleOfSpin2'])
    wave['tc'] = wave.pop('CoalescenceTime')
    wave['distance'] = wave.pop('Distance')
    wave['inclination'] = incl
    wave['polarization'] = psi
    wave['eclipticlatitude'] = wave.pop('EclipticLatitude')
    wave['eclipticlongitude'] = wave.pop('EclipticLongitude')
    wave['coa_phase'] = wave.pop('PhaseAtCoalescence')
    wave['f_final'] = 0.1
    wave['t_obs_start'] = 31536000.
    del wave['PolarAngleOfSpin1'], wave['PolarAngleOfSpin2'], wave['Spin1'],\
wave['Spin2'], wave['InitialPolarAngleL'], wave['Redshift'],\
wave['ObservationDuration'], wave['InitialAzimuthalAngleL'], wave['Cadence']
    bbhx_sigs[f'mbhb{i}'] = wave




def plt(index):

    params = bbhx_sigs[f'mbhb{index}']

    ssb_frame_params = SSB_to_LISA(params['tc'],params['eclipticlongitude'],\
                                   params['eclipticlatitude'],params['polarization'])

    params['tc'] = ssb_frame_params[0]
    params['eclipticlongitude'] = ssb_frame_params[1]
    params['eclipticlatitude'] = ssb_frame_params[2]
    params['polarization'] = ssb_frame_params[3]

    plot_code = f"""
    pycbc_inference_plot_posterior \
        --input-file {cwd}/single/configs/{i}/bbhx_recon.hdf:{'Single_signal_no_GBs'} \
{cwd}/multi/configs/{i}/bbhx_recon.hdf:{'Multiple_signals_no_GBs'} \
        --plot-contours --no-contour-labels --contour-percentiles 90 \
        --output-file {cwd}/plots/{i}_ext_nogbs.png \
        --parameters \
            tc \
            distance \
            eclipticlatitude \
            eclipticlongitude \
            polarization \
            inclination \
        --expected-parameters \
            tc:{params['tc']} \
            distance:{params['distance']} \
            eclipticlatitude:{params['eclipticlatitude']} \
            eclipticlongitude:{params['eclipticlongitude']} \
            polarization:{np.pi + params['polarization']} \
            inclination:{params['inclination']} \
            """
    return plot_code


p=[0]
for i in p:#range(6):
    process = subprocess.Popen(plt(i).split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('{} image created'.format(i))


