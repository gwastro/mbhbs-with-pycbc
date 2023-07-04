## Adapting the PyCBC pipeline to find and infer the properties of gravitational waves from massive black hole binaries in LISA

Connor R. Weaving <sup>1</sup>, Laura K. Nuttall <sup>1</sup>, Ian W. Harry <sup>1</sup>, Shichao Wu <sup>2</sup>, Alexander Nitz <sup>3</sup>

<sub>1. University of Portsmouth, Portsmouth, PO1 3FX, United Kingdom</sub>
<sub>2. Albert-Einstein-Institut, Max-Planck-Institut for Gravitationsphysik, D-30167 Hannover, Germany</sub>
<sub>3. Department of Physics, Syracuse University, Syracuse NY 13244, USA</sub>

## Introduction

The Laser Interferometer Space Antenna (LISA), due for launch in the mid 2030s, is expected to observe gravitational waves (GW)s from merging massive black hole binaries (MBHB)s. These signals can last from days to months, depending on the masses of the black holes, and are expected to be observed with high signal to noise ratios (SNR)s out to high redshifts. We have adapted the PyCBC software package to enable a template bank search and inference of GWs from MBHBs. The pipeline is tested on the LISA data challenge (LDC)'s Challenge 2a ("Sangria"), which contains MBHBs and thousands of galactic binaries (GBs) in simulated instrumental LISA noise. Our search identifies all 6 MBHB signals with more than 98% of the optimal signal to noise ratio. The subsequent parameter inference step recovers the masses and spins within their 90% confidence interval. Sky position parameters have 8 high likelihood modes which are recovered but often our posteriors favour the incorrect sky mode. We observe that the addition of GBs biases the parameter recovery of masses and spins away from the injected values, reinforcing the need for a global fit pipeline which will simultaneously fit the parameters of the GB signals before estimating the parameters of MBHBs.

## License and Citation

This repository is licensed under [GNU General Public License v3.0](https://github.com/gwastro/confusion_noise_3g/blob/main/LICENSE).
We encourage use of these scripts in derivative works. If you use the material provided here, please cite the paper using the reference:

```
@article{Weaving:2023fji,
    author = "Weaving, Connor R. and Nuttall, Laura K. and Harry, Ian W. and Wu, Shichao and Nitz, Alexander",
    title = "{Adapting the PyCBC pipeline to find and infer the properties of gravitational waves from massive black hole binaries in LISA}",
    eprint = "2306.16429",
    archivePrefix = "arXiv",
    primaryClass = "astro-ph.IM",
    month = "6",
    year = "2023"
}
```

In progress:

* zero_noise
* search section

# Setup

To begin, we need to setup our virtual enviroment and install all the
required packages to run our code. We used conda enviroments throughout
our development with the command:

`conda create -n {env_name_here} -c conda-forge gcc_linux-64 gxx_linux-64 gsl lapack=3.6.1 numpy scipy Cython jupyter ipython matplotlib python=3.9`

The packages that you will need to install into this enviroment are:

- [BBHx](https://github.com/mikekatz04/BBHx):

```
git clone https://github.com/mikekatz04/BBHx.git
cd BBHx
python setup.py install
```

- [PyCBC](https://github.com/gwastro/pycbc):

```
git clone https://github.com/gwastro/pycbc.git
cd pycbc
pip install -r requirements.txt
pip install -r companion.txt
pip install .
```

- [BBHX-waveform-model](https://github.com/gwastro/BBHX-waveform-model):

```
git clone https://github.com/gwastro/BBHX-waveform-model.git
cd BBHX-waveform-model
pip install .
```

All links direct you to the respective github pages.


## Dataset downloads (in progress)

# Data and PSD generation

To begin we will generate the data for the type of analysis we would like to investigate. In the *signal_generation* directory we have subdirectories for the different noise types:

* zero_noise
* no_gbs
* with_gbs
* sangria

Each directory (with the exception of *sangria*) has subdirectories for single injections or multiple (named single and multi respectively). Running the script found in these subdirectories will generate the signal injections in the type of noise specified. The *sangria* directory simply converts the Sangria data into a PyCBC format for search and inference.

After the data has been generated, we can now estimate the PSDs by navigating to the *psds* directory. Again, you will find the same directories as in the *signal_generation* directory. Run the script in the desired folder to produce the PSDs for that data.

# Search and Inference
## Search (in progress)

## Inference

### Configuration file generation

Inference is also split into different directories depending on the type of noise and injection(s) you wish to analyse. Navigate to the desired directory and run the script beginning with **gen_configs** to generate the configuration files for all injections. These are stored in the *configs* directory which is split into 6 (0-5) so inference can be run on each signal.

### Running inference

Once your data files and PSDs have been generate, to run inference, use the command on the terminal:

`OMP_NUM_THREADS=1 pycbc_inference --config-files {config_file_name}.ini --output-file bbhx_ref.hdf --force --verbose `

There are many other flags you can use with this command but this is the most basic command to use. The `OMP_NUM_THREADS=1` may also need removing or changing depending on your setup. This command should be ran in the directory that contains the configuration file you're using, but you can easily adjust the file paths to have the inference file output to whatever directory you want.

**IMPORTANT** - The sampler section of the configuration files matches that of the analysis used in the paper. It is recommended that you use multiple cores when running inference to signifcantly reduce the time it takes to complete. We used 32 cores which would take roughly 15 - 20 hours to complete. Alternitvely, if you would rather quickly run inference (for example to test everything is working), reducing the setting `nlive` in the sampler confiuration will also reduce the time taken for inference to complete.

Once inference is complete, you will have a .hdf file in the config directory which now needs some post-processing.

### Post-processing, sky position unfolding

To "unfold" the sky position parameters to their original octants there are two commands you will need to run on your inference .hdf file. The first is:

`pycbc_inference_extract_samples --input-file {inference_file_name}.hdf --output-file bbhx_samples.hdf --force`

Finally, to reconstruct the sky positions from *bbhx_sample.hdf* you need to run the command:

`OMP_NUM_THREADS=1 pycbc_inference_model_stats --input-file bbhx_samples.hdf --output-file bbhx_recon.hdf --reconstruct-parameters --force --config-file bbhx_nogb.ini --verbose`

This will result in the final reconstructed sky position file *bbhx_recon.hdf*. With this file, you can now produce the corner plots with the fully sky position.

# Plotting

