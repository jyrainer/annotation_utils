import os
import json

import copy


def mk_merge_file(folder, categories) :
    """
    이 함수는 coco.json이 들어있는 폴더를 입력으로 받아, json 내용을 불러오게 된다.
    json 내용을 하나로 통일하기 위해서 images 부분과 annotation 부분을 append하여 확장된 하나의 파일 내용을 생성한다.
    annotation의 id와 image_id, images의 id는 고유해야 하므로 차례대로 정수값을 매긴다. 그러므로 원본 버전의 이미지 경로에 대한 id가 다르다.
    단, categories같은 경우 id는 다른데 이름이 같은 경우가 많다. 오류가 발생할 수 있고 많지 않으므로 categories는 본인이 직접 작성한다.    

    args:
        folder_path : folder including json files
        dict : categories infomation

    returns:
        dict : coco json form
    """

    # 기본적 변수 및 리스트
    ann_count = 0
    img_count = 0
    new_images = []
    new_annotations = []

    folder_list = os.listdir(folder)
    #1. 폴더 내의 json을 가져온다. 한 coco.json에 대한 단위
    for coco_list in folder_list :
        if coco_list[-5:] == ".json" :  #json만 가져온다.
            print("coco 파일 :",coco_list)
            json_path = os.path.join(folder, coco_list) # json_path는 개별적 coco.json의 경로
            with open(json_path, 'r') as file :
                coco_data = json.load(file)
                object_coco = copy.copy(coco_data)  # 1.1 object_coco에 복제
                # 2. 이미지 리스트를 불러온다.
                for image_list in object_coco["images"] :
                    save_image_id = image_list['id']
                    image_list['id'] = img_count    #img_count를 img아이디에 할당
                    new_images.append(image_list)   #3. images 연결
                    # 4. annotations 추적
                    for annotation_list in object_coco["annotations"] :
                        copy_annotations_list = copy.copy(annotation_list)
                        if save_image_id == annotation_list["image_id"] :
                            copy_annotations_list['image_id'] = img_count
                            copy_annotations_list['id'] = ann_count
                            new_annotations.append(copy_annotations_list) #5. anns 연결
                            ann_count += 1
                    img_count += 1
        else :
            print("json 파일이 아닌 파일 :",coco_list)
    
    new_all_json = {
        "categories": categories,
        "images": new_images,
        "annotations": new_annotations
    }

    print("Merge End!")
    return new_all_json


if __name__ == "__main__" :
    folder = "/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/vehicle_highway_dataset/result_label_first"            # Fix me
    categories =  [
                            {
                                "id": 1,
                                "name": "vehicle",
                                "supercategory": "vehicle"
                            }
                    ]

    result_path = "/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/vehicle_highway_dataset/result_label_second_merge/coco.json"


    result = mk_merge_file(folder,categories)
    # 파일 저장
    with open(result_path, "w", encoding="utf-8") as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4)
    print("File save.")