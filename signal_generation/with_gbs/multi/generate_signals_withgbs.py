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

sangria_fn = "../datasets/mbhb-unblinded.h5"
mbhb, units = hdfio.load_array(sangria_fn, name="sky/mbhb/cat")
pd.DataFrame(mbhb)
sigs = pd.DataFrame(mbhb).to_dict('records')

# Reading in noiseless data with LDC code
tdi_nn = hdfio.load_array(sangria_fn, name="sky/mbhb/tdi")

tdi_nn = TDI.load(sangria_fn, name="sky/mbhb/tdi")

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
tdi_ts, tdi_descr = hdfio.load_array(sangria_fn, name="obs/tdi")

X = tdi_ts['X']
Y = tdi_ts['Y']
Z = tdi_ts['Z']

A = (Z - X)/np.sqrt(2)
E = (X - 2*Y + Z)/np.sqrt(6)
T = (X + Y + Z)/np.sqrt(3)


# Just noise
noise_A = TimeSeries(A - A_nn, delta_t=5.)
noise_E = TimeSeries(E - E_nn, delta_t=5.)
noise_T = TimeSeries(T - T_nn, delta_t=5.)


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

A_data = TimeSeries(zeros(31536000/5,dtype=float),delta_t=5,epoch=0) + noise_A
E_data = TimeSeries(zeros(31536000/5,dtype=float),delta_t=5,epoch=0) + noise_E
T_data = TimeSeries(zeros(31536000/5,dtype=float),delta_t=5,epoch=0) + noise_T

for i in range(6):
    params = bbhx_sigs[f'mbhb{i}']
    tdi = get_fd_det_waveform_sequence(ifos=['LISA_A','LISA_E','LISA_T'], **params, ref_frame='SSB')
    A_b = tdi['LISA_A'].to_timeseries()
    E_b = tdi['LISA_E'].to_timeseries()
    T_b = tdi['LISA_T'].to_timeseries()

    A_data += A_b
    E_data += E_b
    T_data += T_b

Apsd = A_data.psd(psd_time/sample_length)
Epsd = E_data.psd(psd_time/sample_length)
Tpsd = T_data.psd(psd_time/sample_length)
Apsd = interpolate(Apsd, A_data.delta_f)
Epsd = interpolate(Epsd, E_data.delta_f)
Tpsd = interpolate(Tpsd, T_data.delta_f)
Apsd.save(f'files/A_psd.txt')
Epsd.save(f'files/E_psd.txt')
Tpsd.save(f'files/T_psd.txt')



write_frame(f'files/A_withgbs.gwf', 'LA:LA', A_data)
write_frame(f'files/E_withgbs.gwf', 'LE:LE', E_data)
write_frame(f'files/T_withgbs.gwf', 'LT:LT', T_data)


