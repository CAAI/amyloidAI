from amyloidAI.utils import get_params_fname, maybe_download_parameters, maybe_download_templates

for network_type in ['diagnosis','suvr']:
    for i in range(5):
        params_file = get_params_fname(network_type, i)
        maybe_download_parameters(network_type, i)

maybe_download_templates()