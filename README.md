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
