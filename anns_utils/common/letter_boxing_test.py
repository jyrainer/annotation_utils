import cv2
import os
import numpy as np

# coco, yolo letter box 만들 때 사용 예정
class LetterBox:
    """Resize image and padding for detection, instance segmentation, pose."""

    def __init__(self, new_shape=(640, 640), auto=False, scaleFill=False, scaleup=True, center=True, stride=32):
        """Initialize LetterBox object with specific parameters."""
        self.new_shape = new_shape  # 새로운 이미지의 사이즈
        self.auto = auto            # False 시 new_shape 사이즈에 맞춰서 나옴. True 시 패딩이 덜 됨
        self.scaleFill = scaleFill  # false 해야 ratio 가 유지됨
        self.scaleup = scaleup      # 이미지 resize시 줄이는게아니라 늘리는것일 때, false 시 확장안하고 패딩만함. 설정 픽셀보다 큰 이미지에서는 적용 x
        self.stride = stride        # auto가 true일 때만 동작, 패딩할 픽셀 수 정하는 것임.
        self.center = center        # True : 중앙 배치, False : 왼쪽위에 배치

    def __call__(self, labels=None, image=None):
        """Return updated labels and image with added border."""
        if labels is None:
            labels = {}
        img = labels.get('img') if image is None else image
        shape = img.shape[:2]  # current shape [height, width]
        new_shape = labels.pop('rect_shape', self.new_shape)
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
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        if self.center:
            dw /= 2  # divide padding into 2 sides
            dh /= 2
        if labels.get('ratio_pad'):
            labels['ratio_pad'] = (labels['ratio_pad'], (dw, dh))  # for evaluation

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)) if self.center else 0, int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)) if self.center else 0, int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=(114, 114, 114))  # add border

        if len(labels):
            labels = self._update_labels(labels, ratio, dw, dh)
            labels['img'] = img
            labels['resized_shape'] = new_shape
            return labels
        else:
            return img

    def _update_labels(self, labels, ratio, padw, padh):
        """Update labels."""
        labels['instances'].convert_bbox(format='xyxy')
        labels['instances'].denormalize(*labels['img'].shape[:2][::-1])
        labels['instances'].scale(*ratio)
        labels['instances'].add_padding(padw, padh)
        return labels
    
    
    
if __name__ == "__main__" :
    # 입력 폴더;
    img_folder = "./dataset_test/dataset/letter_boxing/input_img/"
    result_folder = "./dataset_test/dataset/letter_boxing/output_img/"
    
    # 폴더 내 이미지 불러오기
    for folder_name, _, filenames in os.walk(img_folder) :
        for filename in filenames :
            image_path = img_folder + filename      # 이미지의 상대경로 image_path
            
            image = cv2.imread(image_path)          # 이미지 cv2로 불러오기
            
            # 객체 생성 후 초기화
            letterbox = LetterBox(new_shape=(640,640),auto=True,stride=0,scaleFill=False,scaleup=True,center=True)
            
            updated_image = letterbox(image=image)
            
            # 업데이트된 이미지 저장
            cv2.imwrite(result_folder + filename, updated_image)
            