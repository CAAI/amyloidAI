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