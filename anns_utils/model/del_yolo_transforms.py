from ultralytics import YOLO
import torch

def del_compose_from_yolo(model_path):
    model = YOLO(model=model_path)


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

    save_path = model_path.replace('.pt', '_no_transform.pt')
    # Save last, best and delete
    torch.save(model_value, save_path, pickle_module=pickle)
    del model_value


if __name__ == "__main__":
    del_compose_from_yolo("/home/gpuadmin/repo/forked/KTT_Yonsei-Common-AI-python_fastAPI/AI/assets/model/SmokeCls_v1.1.0.pt")