import json
import os
import os.path as osp

import cv2
from tqdm import tqdm


def crop(image_dir, coco_json_path, output_path):
    with open(coco_json_path) as file:
        json_data = json.load(file)

    cate_dict = dict()
    for cate in json_data["categories"]:
        cate_dict[cate["id"]] = cate["name"]
        os.makedirs(output_path + "/" + cate["name"], exist_ok=True)

    # 이미지 순회
    for image in tqdm(json_data["images"]):
        image_path = osp.join(image_dir, image["file_name"])
        image_name = osp.splitext(image["file_name"])[0]
        # error check
        if not osp.exists(image_path):
            print(f"Image not found: {image_path}")
            continue

        image_instance_num = 0
        np_image = cv2.imread(image_path)
        # annotation 순회
        for ann in json_data["annotations"]:
            if ann["image_id"] == image["id"]:
                image_instance_num += 1
                cate_name = cate_dict[ann["category_id"]]
                x, y, width, height = map(int, ann["bbox"])

                cropped_image = np_image[y : y + height, x : x + width]
                try:
                    cv2.imwrite(
                        f"{output_path}/{cate_name}/{image_name}_{image_instance_num}.jpg", cropped_image
                    )
                except:
                    print(f"Error: {image_name}_{image_instance_num}.jpg")


def count_anns_imgs(coco_json_path):
    with open(coco_json_path) as file:
        coco_json = json.load(file)
        print("anns 수:", len(coco_json["annotations"]), "imgs 수:", len(coco_json["images"]))

if __name__ == "__main__" :
    image_path = "/mnt/nas_192/datasets/jyp/datasets/raw_coco2017/train2017"
    json_path = "/mnt/nas_192/datasets/jyp/datasets/raw_coco2017/annotations/instance_person.json"
    output_path = "/mnt/nas_192/datasets/jyp/datasets/raw_coco2017/person_cropped"
    crop(image_path, json_path, output_path)
