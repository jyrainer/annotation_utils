# 슬라이스를 통해 이미지의 배경 의존을 줄여보자!
import os
import json
import copy

import cv2


def quarter_slice_image_and_coco(images_path,coco_path,result_folder) :
    """
    이 함수는 이미지 path와 coco.json 경로를 받아 읽어온 뒤, 이미지를 1사분면...4사분면으로 나누고, 가장 센터까지 포함하여 총 5개의 image로 slice한다.
    그에 따라 라벨 데이터도 완전히 바뀌게 된다.
    또한, 객체가 걸쳐있는 경우나 객체가 없는 이미지의 경우 이미지를 생성하지 않는다.
    이에 따라 이미지가 차지하는 용량을 줄이거나 배경 도메인에 대한 의존성 완화를 기대할 수 있다.
    
    args
        path : images_path, coco.json path
    
    return
        dict : coco annotation form 
        file : divided image files
    
    
    
    """
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    sliced_img_list = []
    anns_info_list = []
    
    exist_cnt_1 = 0
    exist_cnt_2 = 0
    exist_cnt_3 = 0
    exist_cnt_4 = 0
    exist_cnt_5 = 0

    bbox_in_1_list = []
    bbox_in_2_list = []
    bbox_in_3_list = []
    bbox_in_4_list = []
    bbox_in_5_list = []
    
    image_id_cnt = 0
    anns_id_cnt = 0
    
    
    with open(coco_path, 'r') as file :
        json_data = json.load(file)     
        coco_json = copy.deepcopy(json_data)                    # coco_json을 참조하여 값들을 가져옴. json_data는 건들면 X
        
        coco_data["categories"] = coco_json["categories"]       # 카테고리는 그대로 가져옴
        
        for image in coco_json["images"] :                      # coco_json에 존재하는 이미지 정보만큼 for한다.
            slice_width = int(image["width"] / 2)
            slice_height = int(image["height"] / 2)
            image_file_path = image["file_name"]                # 파일 경로
            
            for i in range(5) :
                sliced_img_path = image_file_path[:-4] + "_" + str(i+1) + ".jpg"
                sliced_img_list.append(sliced_img_path)
                
            # 이미지에 해당하는 anns만 정보를 받아와 주자
            for anns in coco_json["annotations"] :
                if anns["image_id"] == image["id"] :
                    anns_info_list.append(anns)
            
            
            # anns 정보를 통해서 몇사분면에 몇개 있는지 파악
            for bbox_info in anns_info_list :
                x1 = bbox_info["bbox"][0]
                x2 = bbox_info["bbox"][0] + bbox_info["bbox"][2]
                y1 = bbox_info["bbox"][1]
                y2 = bbox_info["bbox"][1] + bbox_info["bbox"][3]
                # 1사분면
                if ( x1 > slice_width) and ( y2 < slice_height) :
                    exist_cnt_1 += 1
                    bbox_in_1_list.append(bbox_info)
                # 2사분면
                if ( x2 < slice_width) and ( y2 < slice_height) :
                    exist_cnt_2 += 1
                    bbox_in_2_list.append(bbox_info)
                # 3사분면
                if ( x2 < slice_width) and ( y1 > slice_height) :
                    exist_cnt_3 += 1
                    bbox_in_3_list.append(bbox_info)
                # 4사분면
                if ( x1 > slice_width) and ( y1 > slice_height) :
                    exist_cnt_4 += 1
                    bbox_in_4_list.append(bbox_info)
                # Center
                if ( x1 > slice_width/2) and ( x2 < image["width"]-slice_width/2 ) and (y1>slice_height/2) and ( y2 < image["height"]-slice_height/2) :
                    exist_cnt_5 += 1
                    bbox_in_5_list.append(bbox_info)
            
            
            
            # 1사분면이 존재 시...
            if exist_cnt_1 > 0 :
                # 이미지 생성
                input_path = os.path.join(images_path, image_file_path)
                output_path = os.path.join(result_folder, sliced_img_list[0])

                img = cv2.imread(input_path)
                cropped_img = img[0:slice_height, slice_width:image["width"]]
                cv2.imwrite(output_path, cropped_img)
                
                # 이미지 정보 생성
                image_info = {
                    "id": image_id_cnt,
                    "file_name": sliced_img_list[0],
                    "width":int( image["width"]/2),
                    "height": int(image["height"]/2)
                }
                
                coco_data["images"].append(image_info)
                
                
                for bbox_info_1 in bbox_in_1_list :
                    x1 = bbox_info_1["bbox"][0]
                    x2 = bbox_info_1["bbox"][0] + bbox_info_1["bbox"][2]
                    y1 = bbox_info_1["bbox"][1]
                    y2 = bbox_info_1["bbox"][1] + bbox_info_1["bbox"][3]
                    new_x = x1 - slice_width
                    new_y = y1
                    new_width = bbox_info_1["bbox"][2]
                    new_height = bbox_info_1["bbox"][3]
                    # if new_x < 0 :      # 음수대비
                    #     new_x = 0
                    # if y2 > slice_height :
                    #     new_height = slice_height - y1
                        
                    
                    
                    annotation_info = {
                        "id": anns_id_cnt,
                        "image_id": image_id_cnt,
                        "category_id": bbox_info_1["category_id"],
                        "bbox": [
                            new_x,
                            new_y,
                            new_width,
                            new_height
                        ],
                        "area": new_width * new_height,
                        "iscrowd": 0
                    }

                    anns_id_cnt += 1
                    coco_data["annotations"].append(annotation_info)
                image_id_cnt += 1  
             # 2사분면이 존재 시...
            if exist_cnt_2 > 0 :
                
                # 이미지 생성
                input_path = os.path.join(images_path, image_file_path)
                output_path = os.path.join(result_folder, sliced_img_list[1])

                img = cv2.imread(input_path)
                cropped_img = img[0:slice_height, 0:slice_width]
                cv2.imwrite(output_path, cropped_img)
                
                # 이미지 정보 생성
                image_info = {
                    "id": image_id_cnt,
                    "file_name": sliced_img_list[1],
                    "width":int( image["width"]/2),
                    "height": int(image["height"]/2)
                }
                
                coco_data["images"].append(image_info)
                
                
                for bbox_info_2 in bbox_in_2_list :
                    x1 = bbox_info_2["bbox"][0]
                    x2 = bbox_info_2["bbox"][0] + bbox_info_2["bbox"][2]
                    y1 = bbox_info_2["bbox"][1]
                    y2 = bbox_info_2["bbox"][1] + bbox_info_2["bbox"][3]
                    new_x = x1
                    new_y = y1
                    new_width = bbox_info_2["bbox"][2]
                    new_height = bbox_info_2["bbox"][3]
                    # if x2 > slice_width :      
                    #     new_width = slice_width - x1
                    # if y2 > slice_height :
                    #     new_height = slice_height - y1
                        
                    
                    annotation_info = {
                        "id": anns_id_cnt,
                        "image_id": image_id_cnt,
                        "category_id": bbox_info_2["category_id"],
                        "bbox": [
                            new_x,
                            new_y,
                            new_width,
                            new_height
                        ],
                        "area": new_width * new_height,
                        "iscrowd": 0
                    }

                    anns_id_cnt += 1
                    coco_data["annotations"].append(annotation_info)
                image_id_cnt += 1
            # 3사분면이 존재 시...
            if exist_cnt_3 > 0 :
                # 이미지 생성
                input_path = os.path.join(images_path, image_file_path)
                output_path = os.path.join(result_folder, sliced_img_list[2])

                img = cv2.imread(input_path)
                cropped_img = img[slice_height:image["height"], 0:slice_width]
                cv2.imwrite(output_path, cropped_img)
                
                # 이미지 정보 생성
                image_info = {
                    "id": image_id_cnt,
                    "file_name": sliced_img_list[2],
                    "width":int( image["width"]/2),
                    "height": int(image["height"]/2)
                }
                
                coco_data["images"].append(image_info)
                
                
                for bbox_info_3 in bbox_in_3_list :
                    x1 = bbox_info_3["bbox"][0]
                    x2 = bbox_info_3["bbox"][0] + bbox_info_3["bbox"][2]
                    y1 = bbox_info_3["bbox"][1]
                    y2 = bbox_info_3["bbox"][1] + bbox_info_3["bbox"][3]
                    new_x = x1
                    new_y = y1 - slice_height
                    new_width = bbox_info_3["bbox"][2]
                    new_height = bbox_info_3["bbox"][3]
                    # if x2 > slice_width :      
                    #     new_width = slice_width - x1
                    # if new_y < 0 :
                    #     new_y = 0
                        
                    
                    
                    annotation_info = {
                        "id": anns_id_cnt,
                        "image_id": image_id_cnt,
                        "category_id": bbox_info_3["category_id"],
                        "bbox": [
                            new_x,
                            new_y,
                            new_width,
                            new_height
                        ],
                        "area": new_width * new_height,
                        "iscrowd": 0
                    }

                    anns_id_cnt += 1
                    coco_data["annotations"].append(annotation_info)
                image_id_cnt += 1
            # 4사분면이 존재 시...
            if exist_cnt_4 > 0 :
                # 이미지 생성
                input_path = os.path.join(images_path, image_file_path)
                output_path = os.path.join(result_folder, sliced_img_list[3])

                img = cv2.imread(input_path)
                cropped_img = img[slice_height:image["height"], slice_width:image["width"]]
                cv2.imwrite(output_path, cropped_img)
                
                # 이미지 정보 생성
                image_info = {
                    "id": image_id_cnt,
                    "file_name": sliced_img_list[3],
                    "width":int( image["width"]/2),
                    "height": int(image["height"]/2)
                }
                
                coco_data["images"].append(image_info)
                
                
                for bbox_info_4 in bbox_in_4_list :
                    x1 = bbox_info_4["bbox"][0]
                    x2 = bbox_info_4["bbox"][0] + bbox_info_4["bbox"][2]
                    y1 = bbox_info_4["bbox"][1]
                    y2 = bbox_info_4["bbox"][1] + bbox_info_4["bbox"][3]
                    new_x = x1 - slice_width
                    new_y = y1 - slice_height
                    new_width = bbox_info_4["bbox"][2]
                    new_height = bbox_info_4["bbox"][3]
                    # if x1 < slice_width :      # 음수대비
                    #     new_x = 0
                    # if y1 < slice_height :
                    #     new_y = 0
                        
                    
                    
                    annotation_info = {
                        "id": anns_id_cnt,
                        "image_id": image_id_cnt,
                        "category_id": bbox_info_4["category_id"],
                        "bbox": [
                            new_x,
                            new_y,
                            new_width,
                            new_height
                        ],
                        "area": new_width * new_height,
                        "iscrowd": 0
                    }

                    anns_id_cnt += 1
                    coco_data["annotations"].append(annotation_info)
                image_id_cnt += 1
                
            # 센터에 라벨이 존재 시...
            if exist_cnt_5 > 0 :
                # 이미지 생성
                input_path = os.path.join(images_path, image_file_path)
                output_path = os.path.join(result_folder, sliced_img_list[4])

                img = cv2.imread(input_path)
                cropped_img = img[slice_height // 2:image["height"] - slice_height // 2, slice_width // 2:image["width"] - slice_width // 2]
                cv2.imwrite(output_path, cropped_img)
                
                # 이미지 정보 생성
                image_info = {
                    "id": image_id_cnt,
                    "file_name": sliced_img_list[4],
                    "width":int( image["width"]/2),
                    "height": int(image["height"]/2)
                }
                
                coco_data["images"].append(image_info)
                
                
                for bbox_info_5 in bbox_in_5_list :
                    x1 = bbox_info_5["bbox"][0]
                    x2 = bbox_info_5["bbox"][0] + bbox_info_5["bbox"][2]
                    y1 = bbox_info_5["bbox"][1]
                    y2 = bbox_info_5["bbox"][1] + bbox_info_5["bbox"][3]
                    new_x = x1 - slice_width/2
                    new_y = y1 - slice_height/2
                    new_width = bbox_info_5["bbox"][2]
                    new_height = bbox_info_5["bbox"][3]
                    
                    
                    annotation_info = {
                        "id": anns_id_cnt,
                        "image_id": image_id_cnt,
                        "category_id": bbox_info_5["category_id"],
                        "bbox": [
                            new_x,
                            new_y,
                            new_width,
                            new_height
                        ],
                        "area": new_width * new_height,
                        "iscrowd": 0
                    }

                    anns_id_cnt += 1
                    coco_data["annotations"].append(annotation_info)
                image_id_cnt += 1
                
            # 초기화
            exist_cnt_1 = 0
            exist_cnt_2 = 0
            exist_cnt_3 = 0
            exist_cnt_4 = 0
            exist_cnt_5 = 0
            
            bbox_in_1_list = []
            bbox_in_2_list = []
            bbox_in_3_list = []
            bbox_in_4_list = []
            bbox_in_5_list = []
            
            anns_info_list = []
            sliced_img_list = []
            
            

    return coco_data
    
    
    
    

if __name__ == "__main__" :
    images_path = './images'
    coco_path = './coco.json'
    result_folder = './result'
    
    result = quarter_slice_image_and_coco(images_path, coco_path, result_folder)
    
    with open('./coco_result.json', "w", encoding="utf-8") as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4)