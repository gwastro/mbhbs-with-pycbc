from pycbc.inference.io import loadfile
from pycbc.inference.models import read_from_config
from pycbc.conversions import mchirp_from_mass1_mass2, q_from_mass1_mass2,\
mass1_from_mchirp_q, mass2_from_mchirp_q
from pycbc.waveform import get_fd_det_waveform_sequence
from pycbc import frame
from pycbc.psd.read import from_txt

import pickle
import numpy as np
import matplotlib.pylab as plt

#-------------------------------------------------------------
#-------------------- Reading in data ------------------------
#-------------------------------------------------------------


A_data = '../files/nonoise/A_nonoise.gwf'
E_data = '../files/nonoise/E_nonoise.gwf'
T_data = '../files/nonoise/T_nonoise.gwf'

A = frame.read_frame(A_data, 'LA:LA')
E = frame.read_frame(E_data, 'LE:LE')
T = frame.read_frame(T_data, 'LT:LT')