import os
import json
import copy
import cv2
from tqdm import tqdm


def crop(image_path,coco_json_path, output_path) :
    """coco annotations 형태의 json과 이미지 source를 받아 객체를 Crop 합니다."""
    i = 0
    with open(coco_json_path, 'r') as file:
        json_data = json.load(file)
        coco_json = copy.deepcopy(json_data)
        
        cate_dict = dict()
        for cate in coco_json['categories']:
            cate_dict[cate['id']] = cate['name']
            os.makedirs(output_path + "/" + cate['name'], exist_ok= True)
            
        # 각 bbox마다 반복
        for anns in tqdm(coco_json["annotations"]) :
            i += 1
            cate_name = cate_dict[anns["category_id"]]
            image_id = anns["image_id"]                 # 이미지 고유 아이디
            x,y,width,height = map(int,anns["bbox"])    # 박스좌표
            for imgs in coco_json["images"] :
                if image_id == imgs["id"] :
                    images_path = image_path + '/' + imgs["file_name"]
                    image = cv2.imread(images_path)
                    
                    if image is not None :
                        cropped_image = image[y:y+height, x:x+width]
                        cv2.imwrite(f"{output_path}/{cate_name}/{i}.jpg",cropped_image)
                        #cv2.imwrite(output_path + 'nzia_' +str(i) + ".jpg",cropped_image)
                    else :
                        print("이미지가 없습니다")
                    
        
def count_anns_imgs(coco_json_path) :
    with open(coco_json_path, 'r') as file:
        json_data = json.load(file)
        coco_json = copy.copy(json_data)
        print("anns 수:",len(coco_json["annotations"]),"imgs 수:",len(coco_json["images"]))
        
if __name__ == "__main__" :
    image_path = "/home/ljj/Downloads/nzia_2/raw_image"
    json_path = "/home/ljj/Repo/waffle_hub/scripts/coco_2.json"
    output_path = "/home/ljj/Repo/waffle_hub/scripts/cropped"
    crop(image_path, json_path, output_path)