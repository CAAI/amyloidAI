#!/usr/bin/env python3

import os
import subprocess
from nipype.interfaces.fsl import Threshold, IsotropicSmooth, RobustFOV, BET
from nipype.interfaces import niftyreg
from nipype.interfaces.fsl.maths import ApplyMask
from amyloidAI.utils import get_MRI_template_fname, get_CT_template_fname

def skullstrip_MRI(MRI):
    if not (outfile := MRI.parent.joinpath('ANAT_BET.nii.gz')).exists():
        cmd = ['hd-bet', '-i', str(MRI), '-o', str(outfile)]
        subprocess.check_output(cmd, text=True, env=os.environ.copy())

def skullstrip_CT(CT):

    p = CT.parent

    # Smoothing data
    if not p.joinpath('ANAT_smoothed.nii.gz').exists():
        smoothing = IsotropicSmooth()
        smoothing.inputs.in_file = str(CT)
        smoothing.inputs.sigma = 1
        smoothing.inputs.out_file = f"{p}/ANAT_smoothed.nii.gz"
        smoothing.run()

    # Threshold image
    if not p.joinpath('ANAT_smoothed_0-100.nii.gz').exists():
        clamp = Threshold()
        clamp.inputs.in_file = f"{p}/ANAT_smoothed.nii.gz"
        clamp.inputs.thresh = 0.0
        clamp.inputs.direction = 'below'
        clamp.inputs.out_file = f"{p}/ANAT_smoothed_0.nii.gz"
        clamp.run()

        clamp = Threshold()
        clamp.inputs.in_file = f"{p}/ANAT_smoothed_0.nii.gz"
        clamp.inputs.thresh = 100.0
        clamp.inputs.direction = 'above'
        clamp.inputs.out_file = f"{p}/ANAT_smoothed_0-100.nii.gz"
        clamp.run()

    # Crop to HEAD
    if not p.joinpath('ANAT_smoothed_0-100_crop.nii.gz').exists():
        crop = RobustFOV()
        crop.inputs.in_file = f"{p}/ANAT_smoothed_0-100.nii.gz"
        crop.inputs.out_roi = f"{p}/ANAT_smoothed_0-100_crop.nii.gz"
        crop.inputs.out_transform = f"{p}/crop_transform.nii.gz"
        crop.run()

    # Skull Strip
    if not p.joinpath('ANAT_BET.nii.gz').exists():
        bet = BET()
        bet.inputs.in_file = f"{p}/ANAT_smoothed_0-100_crop.nii.gz"
        bet.inputs.mask = True
        bet.inputs.frac = 0.1
        bet.inputs.out_file = f"{p}/ANAT_BET.nii.gz"
        bet.run()

def skullstrip(ANAT, anat_type):
    if anat_type == "MRI":
        skullstrip_MRI(ANAT)
    else:
        skullstrip_CT(ANAT)

def spatial_align(ANAT, anat_type):

    if anat_type == "CT":
        # Use preprocessed CT to register instead of original
        ANAT = ANAT.parent.joinpath('ANAT_BET.nii.gz')
    
    if not (affine := ANAT.parent.joinpath('ANAT_affine.nii.gz')).exists():
        aff_txt = ANAT.parent.joinpath('aff.txt')
        aff = niftyreg.RegAladin()
        aff.inputs.flo_file = str(ANAT)
        aff.inputs.ref_file = get_MRI_template_fname() if anat_type == "MRI" else get_CT_template_fname()
        aff.inputs.res_file = str(affine)
        aff.inputs.aff_file = str(aff_txt)
        aff.run()

def resample(PET, anat_type):

    p = PET.parent

    # Resample PET
    if not p.joinpath('PET_affine_BET.nii.gz').exists():
        # Resample brain mask
        rsl = niftyreg.RegResample()
        rsl.inputs.ref_file = get_CT_template_fname()
        rsl.inputs.flo_file = f"{p}/ANAT_BET_mask.nii.gz"
        rsl.inputs.trans_file = f"{p}/aff.txt"
        rsl.inputs.inter_val = 'NN'
        rsl.inputs.out_file = f"{p}/mask_affine.nii.gz"
        rsl.run()

        rsl = niftyreg.RegResample()
        rsl.inputs.ref_file = get_CT_template_fname()
        rsl.inputs.flo_file = str(PET)
        rsl.inputs.trans_file = f"{p}/aff.txt"
        rsl.inputs.inter_val = 'LIN'
        rsl.inputs.pad_val = 0.0
        rsl.inputs.out_file = f"{p}/PET_affine.nii.gz"
        rsl.run()

        mask = ApplyMask()
        mask.inputs.in_file = f"{p}/PET_affine.nii.gz"
        mask.inputs.mask_file = f"{p}/mask_affine.nii.gz"
        mask.inputs.out_file = f"{p}/PET_affine_BET.nii.gz"
        mask.run()

def cleanup(PET):
    files = ['ANAT_smoothed','ANAT_smoothed_0','ANAT_smoothed_0-100', 'ANAT_smoothed_0-100_crop', 
             'crop_transform', 'ANAT_BET', 'ANAT_BET_mask','ANAT_affine','PET_affine_BET',
             'mask_affine','PET_affine','PET_affine_BET']
    for f in files:
        if (f_path := PET.parent.joinpath(f+'.nii.gz')).exists():
            f_path.unlink()

    PET.parent.joinpath('aff.txt').unlink()