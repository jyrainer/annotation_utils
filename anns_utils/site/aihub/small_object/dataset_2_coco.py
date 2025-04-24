import os
import json
import glob
from tqdm import tqdm

def convert_to_coco(image_dir, json_dir, target_categories, result_json_path):
    image_id_counter = 0
    annotation_id_counter = 0
    category_mapping = {}
    coco_output = {
        "info": {},
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    while True:
        json_file = glob.glob(os.path.join(json_dir, '*.json'))[0]
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Category info
        for category in data["categories"]:
            if category["class_id"] in target_categories:
                coco_output["categories"].append({
                    "id": category["class_id"],
                    "name": category["class_name"],
                    "supercategory": category["superclass_name"]
                })
        
        break  # 한번만
    
    for json_file in tqdm(glob.glob(os.path.join(json_dir, '*.json')), desc="Processing annotations"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Image info
        for img in data.get("images", []):
            image_id_counter += 1
            coco_output["images"].append({
                "id": image_id_counter,
                "file_name": img["file_name"],
                "width": img["width"],
                "height": img["height"]
            })

            # Annotation info
            for ann in data.get("annotations", []):
                cname = ann.get("category_id")
                if cname in target_categories:
                    annotation_id_counter += 1
                    coco_output["annotations"].append({
                        "id": annotation_id_counter,
                        "image_id": image_id_counter,
                        "category_id": cname,
                        "bbox": list(map(int, ann.get("bbox", []))),
                        "area": int(ann.get("area", 0)),
                        "iscrowd": int(ann.get("iscrowd", 0)),
                        "segmentation": []
                    })

    # Save result
    with open(result_json_path, 'w', encoding='utf-8') as f:
        json.dump(coco_output, f, indent=4, ensure_ascii=False)

    print(f"COCO JSON saved to: {result_json_path}")

if __name__ == "__main__":
    image_dir = "/home/gpuadmin/Downloads/ktt_5/cropped_results/small_object/037.Small object detection을 위한 이미지 데이터/01.데이터/1.Training/1.원천데이터/TS_현관_신발장shoe_rack01"  # Change this to your image directory
    json_dir = "/home/gpuadmin/Downloads/ktt_5/cropped_results/small_object/037.Small object detection을 위한 이미지 데이터/01.데이터/1.Training/2.라벨링데이터/TL_현관_신발장/shoe_rack01"  # Change this to your JSON directory
    target_categories = [574]  # Change this to your target categories
    result_json_path = "coco_output_um.json"  # Change this to your desired output path

    convert_to_coco(image_dir, json_dir, target_categories, result_json_path)