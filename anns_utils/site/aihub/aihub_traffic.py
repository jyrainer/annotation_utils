import os
import json

import cv2

def divid_annotation(annotations: list) -> list[dict]:
    """
    이 함수는 Ai_hub의 교통안전 - 시내도로 관련 데이터셋을 정제하기 위해 필요하다.
    해당 데이터셋에 label 데이터에는 하나의 annotations 정보에 여러개의 bbox 정보가 존재한다.
    이는 coco annotation form과 맞추기 위해 bbox하나하나가 annotation이 되기 위한 함수이다.

    args:
        dict : annotations of coco

    returns:
        dict : new annotations of coco
    """

    new_annotations = []
    new_annotations_count = 1
    category_index = 0

    for annotation in annotations :
        for category in annotation["category_id"] :
            if category in [6,7,8] :                # 자전거/오토바이, 보행자, dontcare 는 추가하지 않음
                category_index += 1
                continue
            else :                                  # 차량으로 분류되는 객체들만 추출
                new_annotations_form = {
                    "id": int(new_annotations_count),
                    "image_id": int(annotation["image_id"]),
                    "category_id": 1,
                    "bbox": [   annotation["bbox"][category_index][0], annotation["bbox"][category_index][1],
                                annotation["bbox"][category_index][2] - annotation["bbox"][category_index][0],
                                annotation["bbox"][category_index][3] - annotation["bbox"][category_index][1]],
                    "iscrowd": 0,
                    "area": (annotation["bbox"][category_index][2] - annotation["bbox"][category_index][0]) * 
                            (annotation["bbox"][category_index][3] - annotation["bbox"][category_index][1])
                }
                new_annotations.append(new_annotations_form)
                category_index += 1
                new_annotations_count += 1
        # for end
        category_index = 0
    # for end
    print("End!")
    return new_annotations


    
def put_width_height(images: list) -> list[dict] :
    """
    현재 images 정보에 이미지의 해상도 정보가 없다는 치명적인 단점이 있다.
    이를 해결하기 위해 file_path를 추적하여 cv툴로 해상도를 넣어줄 것이다.
    """
    new_images = []
    for image in images :
        image_path = "/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Traffic_dataset_aihub/교통안전(Bbox)/result/result_third_step/images/" + image["file_name"] # 이미지의 경로는 다음으로 지정됨.
        try :                           # 이미지가 있는지부터... 없으면 pass됨
            call_img = cv2.imread(image_path)
            height, width, _ = call_img.shape
            new_images_form =   {
                                    "id": int(image["id"]),
                                    "file_name": image["file_name"],
                                    "height": int(height),
                                    "width": int(width)
                                }
            new_images.append(new_images_form)
        except :
            print("이미지가 없습니다 :", image_path)

    return new_images

if __name__ == "__main__":
    coco_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Traffic_dataset_aihub/교통안전(Bbox)/result/result_second_step/coco.json'
    output_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Traffic_dataset_aihub/교통안전(Bbox)/result/result_third_step/coco.json'

    with open(coco_path, 'r') as file:
        coco_data = json.load(file)

    categories = [{"id": 1, "name": "vehicle"}] # 카테고리 정의

    ## 파일 수정 부분
    coco_data["annotations"] = divid_annotation(coco_data["annotations"])     # step 1. annotations를 bbox마다 분리한다.

    coco_data["categories"] = categories                        # step 2. categories는 기호에 맞게 수정한다. divid함수도 수정해야함.

    coco_data["images"] = put_width_height(coco_data["images"]) # step 3. 해상도 부분을 추가해주자...
    ## 파일 수정 부분

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(coco_data, outfile, ensure_ascii=False)