from pycbc.types import TimeSeries
from pycbc.frame import write_frame

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

write_frame(f'files/A_blind.gwf', 'LA:LA', A_data)
write_frame(f'files/E_blind.gwf', 'LE:LE', E_data)
write_frame(f'files/T_blind.gwf', 'LT:LT', T_data)
