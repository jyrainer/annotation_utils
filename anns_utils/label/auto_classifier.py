from pathlib import Path

import numpy as np
import torch
from torch import nn
from glob import glob
import cv2
import os
import shutil
import tqdm

class LetterBox:
    """Resize image and padding for detection, instance segmentation, pose."""

    def __init__(self, new_shape=(640, 640), auto=False, scaleFill=False, scaleup=True, stride=32):
        """Initialize LetterBox object with specific parameters."""
        self.new_shape = new_shape
        self.auto = auto
        self.scaleFill = scaleFill
        self.scaleup = scaleup
        self.stride = stride

    def __call__(self, labels=None, image=None):
        """Return updated labels and image with added border."""
        if labels is None:
            labels = {}
        img = labels.get("img") if image is None else image
        shape = img.shape[:2]  # current shape [height, width]
        new_shape = labels.pop("rect_shape", self.new_shape)
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not self.scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if self.auto:  # minimum rectangle
            dw, dh = np.mod(dw, self.stride), np.mod(dh, self.stride)  # wh padding
        elif self.scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = (
                new_shape[1] / shape[1],
                new_shape[0] / shape[0],
            )  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2
        if labels.get("ratio_pad"):
            labels["ratio_pad"] = (labels["ratio_pad"], (dw, dh))  # for evaluation

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )  # add border

        if len(labels):
            labels = self._update_labels(labels, ratio, dw, dh)
            labels["img"] = img
            labels["resized_shape"] = new_shape
            return labels
        else:
            return img

class AutoBackend(nn.Module):
    def __init__(
        self,
        weights="yolov8n.pt",
        device=torch.device("cpu"),
        dnn=False,
        data=None,
        fp16=False,
        fuse=True,
        verbose=True,
    ):
        """
        MultiBackend class for python inference on various platforms using Ultralytics YOLO.

        Args:
            weights (str): The path to the weights file. Default: 'yolov8n.pt'
            device (torch.device): The device to run the model on.
            dnn (bool): Use OpenCV DNN module for inference if True, defaults to False.
            data (str | Path | optional): Additional data.yaml file for class names.
            fp16 (bool): If True, use half precision. Default: False
            fuse (bool): Whether to fuse the model or not. Default: True
            verbose (bool): Whether to run in verbose mode or not. Default: True

        Supported formats and their naming conventions:
            | Format                | Suffix           |
            |-----------------------|------------------|
            | PyTorch               | *.pt             |
            | TorchScript           | *.torchscript    |
            | ONNX Runtime          | *.onnx           |
            | ONNX OpenCV DNN       | *.onnx dnn=True  |
            | OpenVINO              | *.xml            |
            | CoreML                | *.mlmodel        |
            | TensorRT              | *.engine         |
            | TensorFlow SavedModel | *_saved_model    |
            | TensorFlow GraphDef   | *.pb             |
            | TensorFlow Lite       | *.tflite         |
            | TensorFlow Edge TPU   | *_edgetpu.tflite |
            | PaddlePaddle          | *_paddle_model   |
        """
        super().__init__()
        w = str(weights[0] if isinstance(weights, list) else weights)
        nn_module = isinstance(weights, torch.nn.Module)
        pt, onnx, engine = self._model_type(w)
        fp16 &= pt or onnx or engine or nn_module  # FP16
        stride = 32  # default stride
        model, metadata = None, None
        cuda = torch.cuda.is_available() and device.type != "cpu"  # use CUDA

        # NOTE: special case: in-memory pytorch model
        if nn_module:
            model = weights.to(device)
            model = model.fuse(verbose=verbose) if fuse else model
            if hasattr(model, "kpt_shape"):
                kpt_shape = model.kpt_shape  # pose-only
            stride = max(int(model.stride.max()), 32)  # model stride
            names = (
                model.module.names if hasattr(model, "module") else model.names
            )  # get class names
            model.half() if fp16 else model.float()
            self.model = model  # explicitly assign for to(), cpu(), cuda(), half()
            pt = True
        elif pt:  # PyTorch
            from ultralytics.nn.tasks import attempt_load_weights

            model = attempt_load_weights(
                weights if isinstance(weights, list) else w,
                device=device,
                inplace=True,
                fuse=fuse,
            )
            if hasattr(model, "kpt_shape"):
                kpt_shape = model.kpt_shape  # pose-only
            stride = max(int(model.stride.max()), 32)  # model stride
            names = (
                model.module.names if hasattr(model, "module") else model.names
            )  # get class names
            model.half() if fp16 else model.float()
            self.model = model  # explicitly assign for to(), cpu(), cuda(), half()

        elif onnx:  # ONNX Runtime
            import onnxruntime

            providers = (
                ["CUDAExecutionProvider", "CPUExecutionProvider"]
                if cuda
                else ["CPUExecutionProvider"]
            )
            session = onnxruntime.InferenceSession(w, providers=providers)
            output_names = [x.name for x in session.get_outputs()]
            metadata = session.get_modelmeta().custom_metadata_map  # metadata
        elif engine:  # TensorRT
            try:
                import tensorrt as trt  # noqa https://developer.nvidia.com/nvidia-tensorrt-download
            except ImportError:
                import tensorrt as trt  # noqa
            if device.type == "cpu":
                device = torch.device("cuda:0")
            Binding = namedtuple("Binding", ("name", "dtype", "shape", "data", "ptr"))
            logger = trt.Logger(trt.Logger.INFO)
            # Read file
            with open(w, "rb") as f, trt.Runtime(logger) as runtime:
                meta_len = int.from_bytes(f.read(4), byteorder="little")  # read metadata length
                metadata = json.loads(f.read(meta_len).decode("utf-8"))  # read metadata
                model = runtime.deserialize_cuda_engine(f.read())  # read engine
            context = model.create_execution_context()
            bindings = OrderedDict()
            output_names = []
            fp16 = False  # default updated below
            dynamic = False
            for i in range(model.num_bindings):
                name = model.get_binding_name(i)
                dtype = trt.nptype(model.get_binding_dtype(i))
                if model.binding_is_input(i):
                    if -1 in tuple(model.get_binding_shape(i)):  # dynamic
                        dynamic = True
                        context.set_binding_shape(i, tuple(model.get_profile_shape(0, i)[2]))
                    if dtype == np.float16:
                        fp16 = True
                else:  # output
                    output_names.append(name)
                shape = tuple(context.get_binding_shape(i))
                im = torch.from_numpy(np.empty(shape, dtype=dtype)).to(device)
                bindings[name] = Binding(name, dtype, shape, im, int(im.data_ptr()))
            binding_addrs = OrderedDict((n, d.ptr) for n, d in bindings.items())
            batch_size = bindings["images"].shape[0]  # if dynamic, this is instead max batch size

        if metadata:
            for k, v in metadata.items():
                if k in ("stride", "batch"):
                    metadata[k] = int(v)
                elif k in ("imgsz", "names", "kpt_shape") and isinstance(v, str):
                    metadata[k] = eval(v)
            stride = metadata["stride"]
            task = metadata["task"]
            batch = metadata["batch"]
            imgsz = metadata["imgsz"]
            names = metadata["names"]
            kpt_shape = metadata.get("kpt_shape")
        elif not (pt or nn_module):
            print(f"WARNING ⚠️ Metadata not found for 'model={weights}'")

        self.__dict__.update(locals())  # assign all variables to self

    def forward(self, im, augment=False, visualize=False):
        """
        Runs inference on the YOLOv8 MultiBackend model.

        Args:
            im (torch.Tensor): The image tensor to perform inference on.
            augment (bool): whether to perform data augmentation during inference, defaults to False
            visualize (bool): whether to visualize the output predictions, defaults to False

        Returns:
            (tuple): Tuple containing the raw output tensor, and processed output for visualization (if visualize=True)
        """
        if self.fp16 and im.dtype != torch.float16:
            im = im.half()  # to FP16

        if self.pt or self.nn_module:  # PyTorch
            y = (
                self.model(im, augment=augment, visualize=visualize)
                if augment or visualize
                else self.model(im)
            )
        elif self.onnx:  # ONNX Runtime
            im = im.cpu().numpy()  # torch to numpy
            y = self.session.run(self.output_names, {self.session.get_inputs()[0].name: im})
        elif self.engine:  # TensorRT
            if self.dynamic and im.shape != self.bindings["images"].shape:
                i = self.model.get_binding_index("images")
                self.context.set_binding_shape(i, im.shape)  # reshape if dynamic
                self.bindings["images"] = self.bindings["images"]._replace(shape=im.shape)
                for name in self.output_names:
                    i = self.model.get_binding_index(name)
                    self.bindings[name].data.resize_(tuple(self.context.get_binding_shape(i)))
            s = self.bindings["images"].shape
            assert (
                im.shape == s
            ), f"input size {im.shape} {'>' if self.dynamic else 'not equal to'} max model size {s}"
            self.binding_addrs["images"] = int(im.data_ptr())
            self.context.execute_v2(list(self.binding_addrs.values()))
            y = [self.bindings[x].data for x in sorted(self.output_names)]
        if isinstance(y, (list, tuple)):
            return self.from_numpy(y[0]) if len(y) == 1 else [self.from_numpy(x) for x in y]
        else:
            return self.from_numpy(y)

    def from_numpy(self, x):
        """
        Convert a numpy array to a tensor.

        Args:
            x (np.ndarray): The array to be converted.

        Returns:
            (torch.Tensor): The converted tensor
        """
        return torch.tensor(x).to(self.device) if isinstance(x, np.ndarray) else x

    def warmup(self, imgsz=(1, 3, 640, 640)):
        """
        Warm up the model by running one forward pass with a dummy input.

        Args:
            imgsz (tuple): The shape of the dummy input tensor in the format (batch_size, channels, height, width)

        Returns:
            (None): This method runs the forward pass and don't return any value
        """
        warmup_types = self.pt, self.onnx, self.engine
        if any(warmup_types) and (self.device.type != "cpu"):
            im = torch.empty(
                *imgsz,
                dtype=torch.half if self.fp16 else torch.float,
                device=self.device,
            )  # input
            for _ in range(1):  #
                self.forward(im)  # warmup

    @staticmethod
    def _model_type(p="path/to/model.pt"):
        """
        This function takes a path to a model file and returns the model type

        Args:
            p: path to the model file. Defaults to path/to/model.pt
        """
        sf = list(export_formats().Suffix)  # export suffixes
        types = [s in Path(p).name for s in sf]
        return types

def export_formats():
    """YOLOv8 export formats."""
    import pandas

    x = [
        ["PyTorch", "-", ".pt", True, True],
        ["ONNX", "onnx", ".onnx", True, True],
        ["TensorRT", "engine", ".engine", False, True],
    ]
    return pandas.DataFrame(x, columns=["Format", "Argument", "Suffix", "CPU", "GPU"])

def pre_transform(im, shape=[640, 640], scaleup=False):
    """
    Pre-transform input image before inference.

    Args:
        im (List(np.ndarray)): (N, 3, h, w) for tensor, [(h, w, 3) x N] for list.

    Returns:
        (list): A list of transformed images.
    """
    # same_shapes = len({x.shape for x in im}) == 1
    letterbox = LetterBox(shape, scaleup=scaleup, auto=False, stride=32)
    return [letterbox(image=x) for x in im]


def preprocess(im, device, half=False, shape=[640, 640], scaleup=False):
    not_tensor = not isinstance(im, torch.Tensor)
    if not_tensor:
        im = np.stack(pre_transform([im], shape=shape, scaleup=scaleup))
        im = im[..., ::-1].transpose((0, 3, 1, 2))  # BGR to RGB, BHWC to BCHW, (n, 3, h, w)
        im = np.ascontiguousarray(im)  # contiguous
        im = torch.from_numpy(im)

    im = im.to(device)
    im = im.half() if half else im.float()  # uint8 to fp16/32
    if not_tensor:
        im /= 255  # 0 - 255 to 0.0 - 1.0
    return im

def classify_frame(CLS_model, cropped_frame, device):
    """Run classification model on the cropped frame."""
    img = preprocess(cropped_frame, device=device, shape=[224, 224], scaleup=True)
    img = img if isinstance(img, torch.Tensor) else torch.from_numpy(img).to(device)
    img = img.half() if CLS_model.fp16 else img.float()
    return img



def auto_classify(yolo_cls_model, source_dir, output_dir):
    image_list = glob(source_dir + "/**/*.jpg", recursive=True)

    for image in tqdm.tqdm(image_list):
        image_np = cv2.imread(image)
        
        cls_instance = classify_frame(
            yolo_cls_model, image_np, device=torch.device("cuda:0")
        )
        cls_result = person_classify_model(cls_instance)[0]
        cls_idx = str(cls_result.argmax().item())
        
        result_dir = os.path.join(output_dir, cls_idx)
        os.makedirs(result_dir, exist_ok=True)
        
        shutil.copy(image, os.path.join(result_dir, os.path.basename(image)))
        
        
if __name__ == "__main__":
    yolo_cls_model = "/home/gpuadmin/repo/yolov11/ultralytics/KTTCls_v2.1.0/artifacts/weights/best.pt"
    source_dir = "/home/gpuadmin/repo/KISA/kisa-od-model-trainer/datasets/ktt_yonsei_dormitory_trespass_DetectionDataset_v0.2.0/exports/cropped_images/person"
    output_dir = "/home/gpuadmin/repo/KISA/kisa-od-model-trainer/datasets/ktt_yonsei_dormitory_trespass_DetectionDataset_v0.2.0/exports/cropped_images/person_classified_2"
    
    person_classify_model = (
            AutoBackend(weights=yolo_cls_model, device=torch.device("cuda:0"))
            if yolo_cls_model
            else None
        )
    auto_classify(person_classify_model, source_dir, output_dir)