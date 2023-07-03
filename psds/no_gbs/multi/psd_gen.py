from pycbc.frame import read_frame
from pycbc.psd import interpolate


psd_time = 6307200 # Number of data points for 1yr of data sampled at 5s
sample_length = 31

#-------------------------------------------------------------
#-------------------- Reading in data ------------------------
#-------------------------------------------------------------

A_data = '../../../signal_generation/files/A_nogbs.gwf'
E_data = '../../../signal_generation/files/E_nogbs.gwf'
T_data = '../../../signal_generation/files/T_nogbs.gwf'

A = read_frame(A_data, 'LA:LA')
E = read_frame(E_data, 'LE:LE')
T = read_frame(T_data, 'LT:LT')

#-------------------------------------------------------------
#---------------------Estimating PSDs-------------------------
#-------------------------------------------------------------

Apsd = A_data.psd(psd_time/sample_length)
Epsd = E_data.psd(psd_time/sample_length)
Tpsd = T_data.psd(psd_time/sample_length)
Apsd = interpolate(Apsd, A_data.delta_f)
Epsd = interpolate(Epsd, E_data.delta_f)
Tpsd = interpolate(Tpsd, T_data.delta_f)

#-------------------------------------------------------------
#-----------------------Writing to file-----------------------
#-------------------------------------------------------------

Apsd.save('files/A_psd.txt')
Epsd.save('files/E_psd.txt')
Tpsd.save('files/T_psd.txt')

print('PSDs generated')