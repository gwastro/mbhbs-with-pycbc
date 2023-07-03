from pycbc.frame import read_frame
from pycbc.psd import interpolate


psd_time = 6307200 # Number of data points for 1yr of data sampled at 5s
sample_length = 31

for i in range(6):

    #-------------------------------------------------------------
    #-------------------- Reading in data ------------------------
    #-------------------------------------------------------------

    A_data = f'../../../signal_generation/files/{i}_A_nogbs.gwf'
    E_data = f'../../../signal_generation/files/{i}_E_nogbs.gwf'
    T_data = f'../../../signal_generation/files/{i}_T_nogbs.gwf'

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

    Apsd.save(f'files/A_psd_{i}.txt')
    Epsd.save(f'files/E_psd_{i}.txt')
    Tpsd.save(f'files/T_psd_{i}.txt')

    print(f'Signal {i} generated')