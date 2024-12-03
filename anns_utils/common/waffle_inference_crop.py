import json

import cv2
from tqdm import tqdm


import os

def infer_cropper(infer_json, input_img_folder, result_folder):
    """ waffle inference를 통해 나온 json을 이용하여 객체를 crop합니다."""
    for i in tqdm(infer_json, desc="Processing Images"):
        img_name = list(i.keys())[0]
        img_path = f"{input_img_folder}/{img_name}"

        for anns in list(i.values()):
            count = 0
            if anns and img_path is not None:
                for ann in anns:
                    fp_bbox = ann['bbox']
                    category_num = ann['category_id']
                    image_load = cv2.imread(img_path)
                    bbox = list(map(int, fp_bbox))
                    cropped_img = image_load[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

                    category_folder = f"{result_folder}/{category_num}"
                    os.makedirs(category_folder,exist_ok=True)

                    if count == 0:
                        result_path = f"{category_folder}/{img_name}"
                    else:
                        result_path = f"{category_folder}/{img_name.split('.')[0]}_{count}.jpg"
                    cv2.imwrite(result_path, cropped_img)

                    count += 1
            else:
                pass  # 빈 리스트는 처리하지 않음

        
if __name__ == "__main__" :
    inference_json = "/home/ljj/Repo/waffle_hub/scripts/coco_2.json"
    source = "/home/ljj/Downloads/nzia_2/raw_image"
    result_dir = "/home/ljj/Repo/waffle_hub/scripts/cropped"
    
    
    with open(inference_json, 'r') as file:
        json_data = json.load(file)

    os.makedirs(result_dir, exist_ok=True)
    infer_cropper(json_data,source,result_dir)
    