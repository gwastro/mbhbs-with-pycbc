from pycbc.types import TimeSeries
from pycbc.psd import interpolate

import ldc.io.hdf5 as hdfio

import numpy as np
import pandas as pd

sangria_fn = "../../datasets/mbhb-unblinded.h5"
mbhb, units = hdfio.load_array(sangria_fn, name="sky/mbhb/cat")
pd.DataFrame(mbhb)
sigs = pd.DataFrame(mbhb).to_dict('records')

# Reading in standard noisy data
tdi_ts, tdi_descr = hdfio.load_array(sangria_fn, name="obs/tdi")

X = tdi_ts['X']
Y = tdi_ts['Y']
Z = tdi_ts['Z']

A = (Z - X)/np.sqrt(2)
E = (X - 2*Y + Z)/np.sqrt(6)
T = (X + Y + Z)/np.sqrt(3)


A_data = TimeSeries(A, delta_t=5.)
E_data = TimeSeries(E, delta_t=5.)
T_data = TimeSeries(T, delta_t=5.)


psd_time = 6307200
sample_length = 31


Apsd = A_data.psd(psd_time/sample_length)
Epsd = E_data.psd(psd_time/sample_length)
Tpsd = T_data.psd(psd_time/sample_length)
Apsd = interpolate(Apsd, A_data.delta_f)
Epsd = interpolate(Epsd, E_data.delta_f)
Tpsd = interpolate(Tpsd, T_data.delta_f)
Apsd.save(f'files/A_psd.txt')
Epsd.save(f'files/E_psd.txt')
Tpsd.save(f'files/T_psd.txt')


