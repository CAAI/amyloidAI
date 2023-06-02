import os
import numpy as np
import onnxruntime
import torchio as tio
import amyloidAI.utils as utils
import warnings

#suppress warnings
warnings.filterwarnings('ignore')

def _normalize(PET):
    #norm = tio.RescaleIntensity(percentiles=95)
    norm = tio.Lambda(lambda x: x / np.quantile(x, 0.95))
    clamp = tio.Clamp(0, 1)
    return clamp(norm(PET))

def _resample(PET):
    rsl = tio.Resample(2)
    return rsl(PET)

def run(pet_file):

    # This PET image should be skull stripped and registered to MNI space in 1x1x1 mm resolution.
    pet = tio.ScalarImage(pet_file)
    
    # Normalize
    normalized_pet = _normalize(pet)
    normalized_pet2mm = _normalize(_resample(pet))

    # Predict diagnosis and suvr
    ensemble_diagnosis = predict_diagnosis(normalized_pet)
    ensemble_suvr = predict_suvr(normalized_pet2mm)

    suvr = np.median(ensemble_suvr)
    suvr_std = np.std(ensemble_suvr)
    diagnosis = np.mean(ensemble_diagnosis)
    diagnosis_std = np.std(ensemble_diagnosis)

    return {
        'suvr': suvr,
        'suvr_std': suvr_std,
        'diagnosis': diagnosis,
        'diagnosis_std': diagnosis_std}

def predict_suvr(normalized_pet2mm):

    try:
        suvr = run_inference_case(
            data_file=normalized_pet2mm,
            model_type='suvr')

    except Exception as e:
        print(e)
        suvr = None

    return suvr

def predict_diagnosis(normalized_pet):

    try:
        diagnosis = run_inference_case(
            data_file=normalized_pet,
            model_type='diagnosis')

    except Exception as e:
        print(e)
        diagnosis = None

    return diagnosis


def predict(model, test_data):
    ort_inputs = {model.get_inputs()[0].name: test_data}
    prediction = model.run(None, ort_inputs)
    return prediction[0][0][0]

def run_inference_case(data_file, model_type):

    #test_data = torch.from_numpy(data_file.get_fdata())
    test_data = data_file.tensor
    if model_type == 'suvr':
        # 1,1,128,128,128
        test_data = test_data.float().unsqueeze(0).cpu().numpy()
    else: # diagnosis
        # 1,256,256,256,1
        test_data = test_data.double().unsqueeze(-1).cpu().numpy()

    predictions = []
    for k in range(5):
        model = onnxruntime.InferenceSession(utils.get_params_fname(model_type, k), providers=['CPUExecutionProvider'])
        output = predict(model, test_data)

        if model_type == 'suvr':
            min_suvr, max_suvr = utils.get_SUVR_constants()
            suvr = output*(max_suvr-min_suvr)+min_suvr
            predictions.append(suvr)
        else: # diagnosis
            diagnosis = 1.0 / (1.0 + np.exp(np.negative(output)))
            predictions.append(diagnosis)
        # Release session
        del model

    return predictions
