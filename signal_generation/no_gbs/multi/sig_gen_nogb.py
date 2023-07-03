from pycbc.waveform import get_fd_det_waveform_sequence
from pycbc.types import TimeSeries
from pycbc.types import zeros
from pycbc.frame import write_frame
from pycbc.psd import interpolate

from ldc.common.series import TDI
import ldc.io.hdf5 as hdfio
from ldc.common import tools

import numpy as np
import pandas as pd



sangria_training = "../../../datasets/LDC2_sangria_training_v2.h5"

# Reading in noiseless data with LDC code
tdi_nn = hdfio.load_array(sangria_training, name="sky/mbhb/tdi")

tdi_nn = TDI.load(sangria_training, name="sky/mbhb/tdi")

X_nn = tdi_nn['X']
Y_nn = tdi_nn['Y']
Z_nn = tdi_nn['Z']

A_nn = (Z_nn - X_nn)/np.sqrt(2)
E_nn = (X_nn - 2*Y_nn + Z_nn)/np.sqrt(6)
T_nn = (X_nn + Y_nn + Z_nn)/np.sqrt(3)


tmin=0.
tmax=31536000.
dt=5.
t_range = np.arange(tmin,tmax,dt)

# Reading in standard noisy data
tdi_ts, tdi_descr = hdfio.load_array(sangria_training, name="obs/tdi")

X = tdi_ts['X']
Y = tdi_ts['Y']
Z = tdi_ts['Z']

A = (Z - X)/np.sqrt(2)
E = (X - 2*Y + Z)/np.sqrt(6)
T = (X + Y + Z)/np.sqrt(3)


# Noise including GBs
noise_A_withgb = TimeSeries(A - A_nn, delta_t=5.)
noise_E_withgb = TimeSeries(E - E_nn, delta_t=5.)
noise_T_withgb = TimeSeries(T - T_nn, delta_t=5.)


# Generating GBs to be removed from igb, dgb, vgb files.
for i in ['v','d','i']:

    print(f"{i}gb")

    tdi_gbs = TDI.load(sangria_training, name=f"sky/{i}gb/tdi")

    gb_X = tdi_gbs['X']
    gb_Y = tdi_gbs['Y']
    gb_Z = tdi_gbs['Z']

    gb_A = (gb_Z - gb_X)/np.sqrt(2)
    gb_E = (gb_X - 2*gb_Y + gb_Z)/np.sqrt(6)
    gb_T = (gb_X + gb_Y + gb_Z)/np.sqrt(3)

    noise_A_withgb -= TimeSeries(gb_A, delta_t=5.)
    noise_E_withgb -= TimeSeries(gb_E, delta_t=5.)
    noise_T_withgb -= TimeSeries(gb_T, delta_t=5.)


# Noise without gbs
noise_A = noise_A_withgb
noise_E = noise_E_withgb
noise_T = noise_T_withgb



# Reading in MBHB signals from Sangria blind
sangria_fn = "../../../datasets/mbhb-unblinded.h5"
mbhb, units = hdfio.load_array(sangria_fn, name="sky/mbhb/cat")
pd.DataFrame(mbhb)
sigs = pd.DataFrame(mbhb).to_dict('records')


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



psd_time = 6307200
sample_length = 31

# Injecting BBHx signal with noise from training without GBs. Also saves a psd
# for each gwf (not one psd for all 6 sigs in one gwf).

A_data = TimeSeries(zeros(31536000/5,dtype=float),delta_t=5,epoch=0) + noise_A
E_data = TimeSeries(zeros(31536000/5,dtype=float),delta_t=5,epoch=0) + noise_E
T_data = TimeSeries(zeros(31536000/5,dtype=float),delta_t=5,epoch=0) + noise_T

for i in range(6):
    params = bbhx_sigs[f'mbhb{i}']
    # Read in signals are in the SSB frame
    tdi = get_fd_det_waveform_sequence(ifos=['LISA_A','LISA_E','LISA_T'], **params, ref_frame='SSB')
    A_b = tdi['LISA_A'].to_timeseries()
    E_b = tdi['LISA_E'].to_timeseries()
    T_b = tdi['LISA_T'].to_timeseries()

    A_data += A_b
    E_data += E_b
    T_data += T_b


write_frame(f'../files/A_nogbs.gwf', 'LA:LA', A_data)
write_frame(f'../files/E_nogbs.gwf', 'LE:LE', E_data)
write_frame(f'../files/T_nogbs.gwf', 'LT:LT', T_data)
