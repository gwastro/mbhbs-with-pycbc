import pandas as pd
import numpy as np
import os

from pycbc.conversions import mchirp_from_mass1_mass2, q_from_mass1_mass2
from bbhx.utils.transform import SSB_to_LISA

import ldc.io.hdf5 as hdfio
from ldc.common import tools

# This reads in the highest SNR templates for each trigger in the temp bank
# search.
sangria_fn = "../../../datasets/mbhb-unblinded.h5"
mbhb, units = hdfio.load_array(sangria_fn, name="sky/mbhb/cat")
pd.DataFrame(mbhb)
sigs = pd.DataFrame(mbhb).to_dict('records')


def spin_conv(mag, pol):
    return mag*np.cos(pol)

bbhx_sigs = []
for i in range(6):
    params_inj = sigs[i]

    psi, incl = tools.aziPolAngleL2PsiIncl(params_inj["EclipticLatitude"],
                                        params_inj["EclipticLongitude"],
                                        params_inj['InitialPolarAngleL'],
                                        params_inj['InitialAzimuthalAngleL'])

    params_inj['approximant'] = 'BBHX_PhenomD'
    params_inj['mass1'] = params_inj.pop('Mass1')
    params_inj['mass2'] = params_inj.pop('Mass2')
    params_inj['spin1z'] = spin_conv(params_inj['Spin1'],params_inj['PolarAngleOfSpin1'])
    params_inj['spin2z'] = spin_conv(params_inj['Spin2'],params_inj['PolarAngleOfSpin2'])
    params_inj['tc'] = params_inj.pop('CoalescenceTime')
    params_inj['distance'] = params_inj.pop('Distance')
    params_inj['inclination'] = incl
    params_inj['polarization'] = psi
    params_inj['eclipticlatitude'] = params_inj.pop('EclipticLatitude')
    params_inj['eclipticlongitude'] = params_inj.pop('EclipticLongitude')
    params_inj['coa_phase'] = params_inj.pop('PhaseAtCoalescence')
    params_inj['f_final'] = 0.1
    params_inj['t_obs_start'] = 31536000.
    del params_inj['PolarAngleOfSpin1'], params_inj['PolarAngleOfSpin2'],\
        params_inj['Spin1'], params_inj['Spin2'],\
        params_inj['InitialPolarAngleL'], params_inj['Redshift'],\
        params_inj['ObservationDuration'], params_inj['InitialAzimuthalAngleL'],\
        params_inj['Cadence']
    bbhx_sigs.append(params_inj)


for i in range(len(bbhx_sigs)):

    curr = bbhx_sigs[i]

    up =  SSB_to_LISA(curr['tc'], curr['eclipticlongitude'],
                curr['eclipticlatitude'],
                curr['polarization'])

    curr['tc'] = up[0]
    curr['eclipticlongitude'] = up[1]
    curr['eclipticlatitude'] = up[2]
    curr['polarization'] = up[3]


cwd = os.getcwd()


# This function reads in the reference template parameters from the temp bank
# search and generates a .ini file for the inference run.
def write_configs(i):

    params = bbhx_sigs[i]

    #------------------------------------------------------------

    data_config = f"""
    [data]

    instruments = LISA_A LISA_E LISA_T
    trigger-time = {int(params['tc'])}
    analysis-start-time = {-int(params['tc'])}
    analysis-end-time = {31536000 - int(params['tc'])}
    pad-data=0

    ; strain settings
    sample-rate = 0.2

    ; psd settings
    psd-file= LISA_A:{cwd}/files/A_psd.txt LISA_E:{cwd}/files/E_psd.txt LISA_T:{cwd}/files/T_psd.txt

    ; Frame file channel name for AET
    frame-files = LISA_A:{cwd}/files/A_withgbs.gwf LISA_E:{cwd}/files/E_withgbs.gwf LISA_T:{cwd}/files/T_withgbs.gwf
    channel-name = LISA_A:LA:LA LISA_E:LE:LE LISA_T:LT:LT

    [model]
    name = brute_lisa_sky_modes_marginalize
    base_model = relative
    loop_polarization=0
    low-frequency-cutoff = 1e-4
    high-frequency-cutoff = 1e-2
    epsilon=0.01
    mass1_ref={params['mass1']}
    mass2_ref={params['mass2']}
    mchirp_ref={mchirp_from_mass1_mass2(params['mass1'],params['mass2'])}
    q_ref={q_from_mass1_mass2(params['mass1'],params['mass2'])}
    tc_ref={params['tc']}
    distance_ref= 50000
    spin1z_ref={params['spin1z']}
    spin2z_ref={params['spin2z']}
    inclination_ref={params['inclination']}
    eclipticlongitude_ref={params['eclipticlongitude']}
    eclipticlatitude_ref={params['eclipticlatitude']}
    polarization_ref={params['polarization']}

    [variable_params]
    mchirp=
    q=
    spin1z=
    spin2z=
    tc=
    distance=
    inclination=
    eclipticlongitude=
    eclipticlatitude=
    polarization=

    [static_params]
    approximant=BBHX_PhenomD
    coa_phase={params['coa_phase']}
    t_obs_start=31536000

    [prior-mchirp]
    name=uniform
    min-mchirp=87055.056
    max-mchirp=8705505.633

    [prior-q]
    name=uniform
    min-q=1
    max-q=4

    [prior-spin1z]
    name = uniform
    min-spin1z=-0.99
    max-spin1z=0.99

    [prior-spin2z]
    name = uniform
    min-spin2z=-0.99
    max-spin2z=0.99

    [prior-tc]
    name = uniform
    min-tc = {params['tc'] - 86400}
    max-tc = {params['tc'] + 86400}

    [prior-inclination]
    ; inclination prior
    name = sin_angle

    [prior-eclipticlongitude]
    name=uniform
    min-eclipticlongitude=0
    max-eclipticlongitude=1.5707963267948966

    [prior-eclipticlatitude]
    name=cos_angle
    min-eclipticlatitude=0
    max-eclipticlatitude=1.5707963267948966

    [prior-polarization]
    name=uniform
    min-polarization=0
    max-polarization=1.5707963267948966

    [prior-distance]
    name = uniform
    min-distance = 1000
    max-distance = 100000

    [waveform_transforms-mass1+mass2]
    name=mchirp_q_to_mass1_mass2

    [sampler]
    name=dynesty
    nlive=3000
    dlogz=0.1
    checkpoint_time_interval=300

    [sampler-burn_in]
    burn-in-test=nacl & max_posterior
"""
    return data_config



# This loop calls the function that creates the config files for each signal
# found in Sangria
for i in range(6):
    data_config = write_configs(i)
    with open(f'configs/{i}/bbhx_withgbs.ini', 'w') as f:
        f.write(data_config)

    print(f'Sample config for signal {i} complete!')

