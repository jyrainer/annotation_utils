import os
import json


def convert_to_coco_format(data_folder, output_file, categories):
    """
    AI_hub에서 화재씬 데이터를 처리할 때 사용한다.
    라벨 데이터가 raw한 형태로 있으므로, 우리가 사용하는 coco annotation format을 변환하는 코드이다.


    args:
        folder : raw data folder including ai_hub data
        path : output_file path
        categories : infomation like cls, index

    returns:
        dict : coco.json file
    """
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": categories
    }

    error_counter = 0
    image_id = 1
    annotation_id = 1
    class_index = 0
    
    for root, _, files in os.walk(data_folder):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    data = json.load(f)

                # image_info 생성
                image_info = {
                    "id": image_id,
                    "file_name": data["image"]["filename"],
                    "width": data["image"]["resolution"][0],
                    "height": data["image"]["resolution"][1],
                    "date_captured": data["image"]["date"],
                    "path": data["image"]["path"]
                }
                coco_data["images"].append(image_info)

                # data안에 있는 annotation 개수만큼 annotation정보를 넣는다. 하나의 annotation은 객체의 위치정보를 가진다.
                for annotation in data["annotations"]:
                    # bbox 정보가 있는 경우
                    if "box" in annotation:
                        x, y, width, height = annotation["box"] # x1, y1, x2, y2 -> x2-x1 = width 
                        width = width - x
                        height = height - y
                    # Segmentation 정보가 있는 경우 최대 최솟값으로 bbox로 변환
                    elif "polygon" in annotation:
                        try :
                            polygon = annotation["polygon"]
                            x_values = [point[0] for point in polygon]
                            y_values = [point[1] for point in polygon]
                            x = min(x_values)
                            y = min(y_values)
                            width = max(x_values) - x
                            height = max(y_values) - y
                        except :
                            error_counter += 1
                            print("라벨링 에러 발생 지점 : ", data["image"]["filename"])
                            continue
                    # 받은 정보들로 annotation 정보 생성
                    
                    # 아래 if문은 class를 임의 mapping 함. 123 인덱스는 1로 통일(연기) 4는 2로 매핑(불꽃)
                    if int(annotation["class"]) == 1 :
                        class_index = 1  #smoke
                    elif int(annotation["class"]) == 2 :
                        class_index = 1 #smoke
                    elif  int(annotation["class"]) == 3 :
                        class_index = 1  #smoke
                    elif int(annotation["class"]) == 4 :
                        class_index = 2  #flame
                    elif int(annotation["class"]) == 5 :
                        print("구름 label 위치 : ", data["image"]["filename"])
                        continue
                    
                    annotation_info = {
                        "id": annotation_id,
                        "image_id": image_info["id"],
                        "category_id": class_index,
                        "bbox": [x, y, width, height],
                        "iscrowd": 0,
                        "area": width * height
                    }
                    coco_data["annotations"].append(annotation_info)
                    annotation_id += 1

                image_id += 1
    print("총 annotation 개수 :", annotation_id - 1)
    print("총 image 개수 :", image_id-1)
    print("End!")
    return coco_data

if __name__ == "__main__" :
    # data 폴더 및 coco.json 생성 위치 설정
    data_folder = "/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/label_500"                       # Fix me
    output_file = "/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/dataset_firescene_500/coco.json" # Fix me
    # 현재 데이터는 category에 대한 정보가 없으므로 직접 지정해주어야 함
    categories = [
        {"id": 1, "name": "smoke"},
        {"id": 2, "name": "flame"}
    ]
    coco_data = convert_to_coco_format(data_folder, output_file, categories)
with open(output_file, "w", encoding="utf-8") as outfile:
    json.dump(output_file, outfile, ensure_ascii=False, indent=4)