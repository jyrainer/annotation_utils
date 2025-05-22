from ultralytics import YOLO
import torch

model = YOLO(model='/home/gpuadmin/repo/forked/KTT_Yonsei-Common-AI-python_fastAPI/AI/assets/model/PersonWalljumpCls_v2.2.0.pt')


"""Save model checkpoints based on various conditions."""
a = model.ckpt
from copy import deepcopy
import datetime

model_value = deepcopy(a)
del model_value['model'].transforms

model_value['model'] = model_value['model'].half()

ckpt = {
        'epoch': -1,
        'best_fitness': None,
        'model': model_value,
        'ema': None,
        'updates': None,
        'optimizer': None,
        'train_args': a['train_args'],  # save as dict
        'date': datetime.datetime.now().isoformat(),
        'version': a['version']
    }

# Use dill (if exists) to serialize the lambda functions where pickle does not do this
try:
    import dill as pickle
except ImportError:
    import pickle

# Save last, best and delete
torch.save(model_value, '/home/gpuadmin/repo/forked/KTT_Yonsei-Common-AI-python_fastAPI/AI/assets/model/PersonWalljumpCls_v2.2.1.pt', pickle_module=pickle)
del model_value