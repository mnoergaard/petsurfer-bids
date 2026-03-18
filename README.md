# PETsurfer-BIDS

## Table of Contents

- [Overview](#key-capabilities)
- [Usage](#usage)
- [Key capabilities](#key-capabilities)
- [Development](#development)
- [Recommended citation](#recommended-citation)

## Overview

This project is an encapsulation of the functionality in PETsurfer
within an easy-to-use BIDS app.  PETSurfer is a set of tools within
the FreeSurfer environement for end-to-end integrated MRI-PET
analysis, including: 
- motion correction (MC)
- PET-MRI registration
- reference-region and invasive kinetic modeling
- partial volume correction (PVC)
- MRI distortion correction
- group analysis in ROI, volume, and surface spaces
- correction for multiple comparisons.

The Brain Imaging Data Structure (BIDS) is a simple and
intuitive way to organize and describe neuroimaging data; many
researchers make their data available to the community in BIDS format
via [OpenNeuro](https://openneuro.org/). Software developers have created BIDS
apps which exploits the BIDS structure to write analysis routines that
seamlessly traverse through a BIDS tree, analyzing each data point found, and
storing the result in BIDS format so that other applications can provide further
analysis. 

PETsurfer-BIDS is a BIDS app builds upon the outputs of
[PETPrep](https://github.com/nipreps/petprep) and
[bloodstream](https://github.com/mathesong/bloodstream). 

PETsurfer functionality is divided between petsurfer-bids and PETPrep. PETPrep runs the
pre-processing aspects (MC, PET-MRI registration, PVC, sampling to
template spaces) whereas petsurfer-bids runs voxel-wise smoothing,
kinetic modeling, and group analysis. If the kinetic modeling is
invasive, then bloodstream can be run to create the arterial input
function (AIF) used by PETsurfer kinetic modeling. The ultimate goal
of this project is to allow users to put their PET data into BIDS
format (or download PET data from OpenNeuro) and then provide
end-to-end PET analysis through BIDS apps.

See the [PETsurfer wiki](https://surfer.nmr.mgh.harvard.edu/fswiki/PetSurfer)
for more information.

## Key capabilities

* **Integrated MRI-PET workflow**: registration, motion correction,
  ROI/volume/surface analysis, MRI gradient distortion correction.
* **Kinetic modeling (KM)**: MRTM1, MRTM2, and invasive Logan modeling,
  including MA1.
* **Partial volume correction (PVC)** methods: Symmetric GTM (SGTM), two-compartment (Meltzer),
  three-compartment (Muller-Gartner / MG), and RBV; implementations also account for
  tissue fraction effect (TFE).
* **Three-space approach** for voxel-wise work: cortical and subcortical GM analyzed separately
  (LH cortex, RH cortex, subcortical GM) to leverage surface-based operations.

## Usage

PETsurfer-BIDS can perform both participant-level analyses and group-level
analyses.  It is invoked via `petsurfer-km` and conforms to the BIDS app interface

```
petsurfer-km bids_dir output_dir {participant,group}
```

### Installation

Like all other BIDS apps, PETsurfer-BIDS is indented to be run inside a 
*container* (i.e. [docker](https://www.docker.com/),
[apptainer](https://apptainer.org/), or [singularity](https://sylabs.io/singularity/))

The container registry is located [here](https://hub.docker.com/r/freesurfer/petsurfer-bids/tags)

You can pull the `v0.1.3` of the container:

**With Docker**:
```
docker pull freesurfer/petsurfer-bids:0.1.3
```

**With Apptainer**:
```
apptainer pull petsurfer-bids-0.1.3.sif docker://freesurfer/petsurfer-bids:0.1.3
```

**With Singularity CE**:
```
singularity pull petsurfer-bids-0.1.3.sif docker://freesurfer/petsurfer-bids:0.1.3
```

When running PETsurfer-BIDS inside a container, you will need to *bind mount*
relevant input and output paths.  At a minimum, you will need to *bind mount*:
- The input data directory (`bids_dir`)
- The output data directory (`output_dir`)
- The location of the FreeSurfer license file, which should be mounted to
  `/usr/local/freesurfer/8.1.0-1/.license` inside the container.  If you don't
  have a FreeSurfer license file, you can apply for and receive one immediately
  [here](https://surfer.nmr.mgh.harvard.edu/registration.html).

Refer to the documentation for your container platform
([Docker](https://docs.docker.com), [Singularity/SingularityCE](https://docs.sylabs.io),
or [Apptainer](https://apptainer.org/docs)) for more information.

PETsurfer-BIDS can also be run locally by installing and configuring a
FreeSurfer and python environment.  See the [Development](#development) for
instructions.

### Participant-level analysis

PETsurfer-BIDS currently supports the following kinetic models:
- MRTM1
- MRTM2
- Logan
- Logan-MA1

Multiple models can be executed simultaneously and can be specified using the
`--km-method` flag.

MRTM2 relies on the rate constant of the reference region (`k2prime`) estimated
in MRTM1. Specifying MRTM2 automatically includes MRTM1.

For each kinetic model specified, the following analyses will be performed:
- ROI based
- Volumetic (voxel) based
- Surface based

The volumetic analysis can be disabled by specifying `--no-vol`.  The surface
based analysis can be disabled by specifying `--no-surf`.  The flags `--lh` and
`--rh` can be used to only run only the left or right hemisphere of the surface
based analysis

All kinetic models rely on the outputs of [PETPrep](https://github.com/nipreps/petprep).
Volumetic analyses are performed in `MNI152NLin2009cAsym` space and
surface-based analyeses are performed in `fsaverage` space.  PETPrep must therefore 
must produce outputs in these spaces.  To be able to perform a full
PETsurfer-BIDS analysis, including volumetric and surface based analyses, be
sure to include the following flag when running PETPrep:
`--output-spaces MNI152NLin2009cAsym fsaverage`.  Refer to the 
[PETPrep documentation](https://petprep.readthedocs.io/en/latest/) for further
details.

The location of the PETPrep output directory is by default assumed to be
`<bids_dir>/derivatives/petprep`, however the location can be specified using the
`--petprep-dir` flag.

For MRTM1 modelling, a comma seperated list of reference regions can be
specified using the `--mrtm1-ref` flag
(default: `Left-Cerebellum-Cortex,Right-Cerebellum-Cortex`).

For MRTM2 modelling, a comma seperated list of high-binding regions can be
specified using the `--mrtm2-hb` flag (default: `Left-Putamen,Right-Putamen`)

For both the `--mrtm1-ref` and `--mrtm2-hb` flags, the region names provided
should correspond to colum heading names in the `*_tacs.tsv` outputs from ***
PETPrep.

For Logan and Logan-MA1 modelling, PETsurfer-BIDS also relies on the outputs of
[bloodstream](https://github.com/mathesong/bloodstream).  The location of the
bloodstream output directory is by default assumed to be `<bids_dir>/derivatives/bloodstream`,
however the location can be specified using the `--bloodstream-dir` flag.

### Group-level analysis

TODO

## Development

- Setup a [FreeSurfer 8.1.0+ environment](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
- Setup a python 3.8+ environment.  For example, using [miniforge](https://conda-forge.org/download/)

```
conda create -n petsurfer-bids python=3.8 -y
conda activate petsurfer-bids
git clone git@github.com:freesurfer/petsurfer-bids.git
cd petsurfer-bids
pip install -e .
```

## Recommended citation

If you use PETSurfer, please cite:

* Greve, D.N., et al. (2014). *Cortical surface-based analysis reduces bias and variance in kinetic modeling of brain PET data.* NeuroImage, 92, 225-236.
* Greve, D.N., et al. (2016). *Different partial volume correction methods lead to different conclusions: An 18F-FDG-PET study of aging.* NeuroImage, 132, 334-343.
