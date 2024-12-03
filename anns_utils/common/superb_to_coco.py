import os
import json
import copy



def sup_to_coco(meta_path,project_json_path) :

    """
    이 함수는 우리 회사에서 사용하는 데이터셋인 superb에서 COCO annotation format으로 변환하는 함수이다.
    
    args :
        path : meta_path, project.json path
    
    return :
        dict : coco annotation form
    """
    # 변수 선언
    img_id = 0              # images의 id 및 annotations의 image_id
    ann_id = 0              # annotations의 id
    cat_id = 1              # categories의 id
    cat_lists = []          # 카테고리 리스트
    cat_num = 1             # 카테고리 번호

    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    # 먼저, Categories 설정
    with open(project_json_path, 'r') as ca:
        pro_data = json.load(ca)
        # 카테고리 개수만큼 반복
        for category in pro_data["object_detection"]["object_classes"] :
            category_name = category["name"]        # categories의 name이 될 아이
            category_super_name = category_name     # 임시로, supercategory 도 같은 이름이 될 듯
            cate_id = cat_id                        # categories의 id가 될 아이
            category_info = {
                "id": cate_id,
                "name": category_name,
                "supercategory": category_super_name
            }
            coco_data["categories"].append(category_info)               # 카테고리 실제연결
            cat_lists.append(category_name)                              # cat_list에 카테고리들이 모여있다
            cat_id += 1
    
    for dirpath, dirnames, filenames in os.walk(meta_path):             # meta 폴더 내의 파일을 순회하여 읽어온다.
        for file_in_meta in filenames:
            meta_info = os.path.join(dirpath, file_in_meta)             # meta_info는 읽어온 파일의 경로
            img_name = file_in_meta[:-5]                                # 이미지 이름은 메타 파일명과 동일함.
            if os.path.isfile(meta_info):                               # meta 파일일 경우에만 처리한다.
                # images 부분
                with open(meta_info, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)  
                    file_name = json_data["data_key"][1:]               # images의 file_name이 될 아이
                    width = json_data["image_info"]["width"]            # images의 width가 될 아이
                    height = json_data["image_info"]["height"]          # images의 height가 될 아이
                    images_id = img_id                                  # images의 id가 될 아이

                    image_info = {
                        "id": images_id,
                        "file_name": file_name,
                        "width": width,
                        "height": height
                    }
                    coco_data["images"].append(image_info)              # 이미지 실제 연결

                    anns_file = json_data["label_path"][0]
                    # annotations 부분
                    with open(anns_file, 'r') as an:
                        anns_data = json.load(an)                       # annotations의 내용이 들어있는 dict
                        for label_info in anns_data["objects"] :            # bbox 개수만큼 반복
                            image_id = img_id                               # annotations의 images_id가 될 녀석
                            bbox_info = label_info["annotation"]["coord"]   # annotations의 x,y,width,hegiht가 dict로 들어있음
                            area = bbox_info["width"] * bbox_info["height"] # annotations의 area가 될 녀석
                            # 클래스가 몇번인지 찾자...
                            for cat_list in cat_lists :
                                if cat_list == label_info["class_name"] :
                                    category_id = cat_num                   # annotations의 category_id가 될 녀석
                                cat_num += 1

                            annotation_info = {
                                "id": ann_id,
                                "image_id": image_id,
                                "category_id": category_id,
                                "bbox": [
                                    bbox_info["x"],
                                    bbox_info["y"],
                                    bbox_info["width"],
                                    bbox_info["height"]
                                ],
                                "area": area,
                                "iscrowd": 0
                            }
                            coco_data["annotations"].append(annotation_info)              # 이미지 실제 연결
                            cat_num = 1
                            ann_id += 1
                    img_id += 1
    
    return coco_data






if __name__ == "__main__" :

    meta_path = './meta'                        #fix me            
    project_json_path = './project.json'        #fix me  
    result_path = './result.json'               #fix me

    result = sup_to_coco(meta_path,project_json_path)

    with open(result_path, "w", encoding="utf-8") as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4)




    print("End!")