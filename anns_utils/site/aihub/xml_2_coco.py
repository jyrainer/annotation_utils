import os
import json

import xml.etree.ElementTree as ET

def convert_to_coco(xml_data,categories):
    """
    본 함수는, Aihub에서 교통정리 - 고속도로의 라벨링 데이터를 coco annotations format으로 바꾸기 위한 함수이다.
    해당 라벨링 데이터는 정해진 것이 없는 커스텀 xml 형식으로 추정되며,
    coco.json에서 필수적인 요소들만 추출할 수 있도록 설정하였다.
    
    args :
        folder  : json을 포함한 folder_path가 필요
        dict    : categories 정보를 따로 지정해주어야 함.

    returns :
        dict    : coco_data
    """

    coco_data = {
        "categories": [],
        "images": [],
        "annotations": []
    }

    coco_data["categories"].append(categories)
    image_id = 0
    annotation_id = 0

    # XML 데이터 파싱
    for image_info in xml_data.findall("image"):
        image_name = image_info.get("name")
        image_width = int(image_info.get("width"))
        image_height = int(image_info.get("height"))

        # 이미지 정보 추가
        coco_image = {
            "id": image_id,
            "file_name": image_name,
            "width": image_width,
            "height": image_height
        }
        coco_data["images"].append(coco_image)

        # 객체 정보 추가
        for box_info in image_info.findall("box"):
            label = box_info.get("label")
            xtl = float(box_info.get("xtl"))
            ytl = float(box_info.get("ytl"))
            xbr = float(box_info.get("xbr"))
            ybr = float(box_info.get("ybr"))

            # COCO 어노테이션 형식에 맞게 변환
            coco_annotation = {
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 1,
                "bbox": [xtl, ytl, xbr - xtl, ybr - ytl],
                "area": (xbr - xtl) * (ybr - ytl),
                "iscrowd": 0
            }
            coco_data["annotations"].append(coco_annotation)

            annotation_id += 1

        image_id += 1

    return coco_data



if __name__ == "__main__" :

    # Fix folder_path, categories
    folder_path = "/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/vehicle_backup/highway/바운딩박스/end/raw_label"
    categories = {
        "id": 1,
        "name": "vehicle",
        "supercategory": "vehicle"
        }




    folder_list = os.listdir(folder_path)
    for xml_list in folder_list :
        xml_file_path = os.path.join(folder_path, xml_list)
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        coco_data = convert_to_coco(root,categories)
        output_json_path = "./result_label_first/" + xml_list[:-4] +".json"  # 저장할 JSON 파일 경로
        with open(output_json_path, "w") as json_file:
            json.dump(coco_data, json_file)