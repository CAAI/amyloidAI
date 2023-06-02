# amyloidAI
Estimation of brain amyloid accumulation using deep learning in clinical [<sup>11</sup>C]PiB PET imaging.

The manuscript is under consideration for publication.

## Usage:
The algorithms require the PET image to be skull stripped and resampled to MNI space in 1x1x1 mm<sup>3</sup> resolution and 256x256x256 matrix.

The templates to do this guided by CT or MRI are supplied. If the PET image is already preprocessed, simply call:

`amyloidAI -i <PET.nii.gz>`

To run the preprocessing as part of the algorithm you need to supply a CT or an MRI image that is aligned with the PET image:

`amyloidAI -i <PET.nii.gz> --CT <CT.nii.gz>`

or

`amyloidAI -i <PET.nii.gz> --MRI <MRI.nii.gz>`

## Algorithm output and interpretation
The algorithm outputs (and prints) a dictionary with the keys: `suvr`, `suvr_std`, `diagnosis`, `diagnosis_std`. 
The main output, suvr and diagnosis, is the median and mean, respectively, of the 5-fold ensemble inference. The *_std outputs are the standard deviation of the five predicted values.

### SUVr
SUVr < 1.35 can be interpreted as amyloid negative and > 1.35 as amyloid positive. A high standard deviation indicates less model certainty for the diagnosis of the patient.

### Diagnosis
A diagnosis value < 0.5 indicates amyloid negative and > 0.5 amyloid positive. Here too, a larger standard deviation indicates less certainty for the diagnosis.