from urllib.request import urlopen
import os
from amyloidAI.paths import folder_with_parameter_files

def get_params_fname(network_type, fold):
    assert network_type in ('diagnosis','suvr'), "Wrong network type. Has to be diagnosis or suvr"
    return os.path.join(folder_with_parameter_files, f"{network_type}_k{fold}.onnx")

def maybe_download_parameters(network_type, fold=0, force_overwrite=False):
    """
    Downloads the parameters for some fold if it is not present yet.
    :param network_type: One of diagnosis or suvr
    :param fold:
    :param force_overwrite: if True the old parameter file will be deleted (if present) prior to download
    :return:
    """

    assert 0 <= fold <= 4, "fold must be between 0 and 4"

    if not os.path.isdir(folder_with_parameter_files):
        maybe_mkdir_p(folder_with_parameter_files)

    out_filename = get_params_fname(network_type, fold)

    if force_overwrite and os.path.isfile(out_filename):
        os.remove(out_filename)

    if not os.path.isfile(out_filename):
        url = f"https://zenodo.org/record/7997708/files/{network_type}_k{fold}.onnx?download=1"
        print("Downloading", url, "...")
        data = urlopen(url).read()
        with open(out_filename, 'wb') as f:
            f.write(data)

def get_CT_template_fname():
    return os.path.join(folder_with_parameter_files, 'avg_CT_template.nii.gz')

def get_MRI_template_fname():
    return os.path.join(folder_with_parameter_files, 'avg_MRI_template.nii.gz')

def maybe_download_templates():
    out_CT_filename = get_CT_template_fname()
    out_MRI_filename = get_MRI_template_fname()

    for out_filename, url in zip([out_CT_filename, out_MRI_filename], ["https://zenodo.org/record/7997708/files/avg_template.nii.gz?download=1", "https://zenodo.org/record/7997708/files/mni_icbm152_t1_tal_nlin_sym_09a.nii?download=1"]):
        if not os.path.isfile(out_filename):
            print("Downloading", url, "...")
            data = urlopen(url).read()
            with open(out_filename, 'wb') as f:
                f.write(data)

def get_SUVR_constants():
    # Constants used for SUVR rescaling
    min_suvr = 0.78
    max_suvr = 3.69
    return min_suvr, max_suvr

def maybe_mkdir_p(directory):
    splits = directory.split("/")[1:]
    for i in range(0, len(splits)):
        if not os.path.isdir(os.path.join("/", *splits[:i+1])):
            os.mkdir(os.path.join("/", *splits[:i+1]))