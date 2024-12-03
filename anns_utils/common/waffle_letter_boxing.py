import os
import cv2
import json
import copy

from tqdm import tqdm

def waffle_dataset_optimizer (dataset_folder, resolution = 640) :
    """
    본 함수는 waffle dataset 폴더를 입력으로 둘 때, 이미지 사이즈 및 라벨정보를 변경하여, 데이터셋 archive 시 데이터 용량에 대한 이점을 제공합니다.
    학습 시 640x640 을 input size로 넣는데, 한 변의 최대 길이를 입력으로 두며, 나머지 변은 줄어들거나 늘어난 ratio에 비례해 재조정됩니다.
    waffle 에서 제공하는 dataset.draw_annotations() 함수를 이용하여 annotation이 제대로 쳐져있는지 확인할 수 있습니다.
    dataset의 모든 파일을 복사하는 것은 시간이 오래 걸리기에, 기존 dataset이 변경되므로 데이터 관리를 위해 백업을 해주세요.

    Args:
        dataset_folder (str): waffle 데이터셋 경로.
            반드시 annotations, images, raw 폴더를 가지고 있어야 한다.
        
        resolution (int): 재조정될 한변의 최대 길이. 640이 default
        

    """

    annotations_folder = f"{dataset_folder}/annotations/"
    images_folder = f"{dataset_folder}/images/"
    raw_folder = f"{dataset_folder}/raw/"   # 실제 이미지

    
    # Images 폴더 내 조회
    for root_image, dirs, files in os.walk(images_folder) :
        for file_name in tqdm(files, desc="Processing Images"):
            file_path = os.path.join(root_image, file_name)

            width_is_longer = False         # width가 hegiht보다 크면 True
            
            # Image 정보 json파일 조회
            with open(file_path, 'r') as file:
                image_json_data = json.load(file)
                # 기본 정보 저장
                image_width = image_json_data["width"]
                image_height = image_json_data["height"]
                image_path = image_json_data["file_name"]
                image_id = image_json_data["image_id"]
                
                # 긴 변을 max_line, 작은 변을 min_line으로 정수 저장
                max_line = max(image_height,image_width)
                min_line = min(image_height,image_width)
                
                d_line = resolution/max_line  # ratio 정의
                
                set_max_line = int(max_line * d_line)   # 재 정의된 긴 변
                set_min_line = int(min_line * d_line)   # 재 정의된 짧은 변
                
                # image_json_data에 해당 내용 새로 써주기
                if image_width >= image_height :
                    width_is_longer = True
                    image_json_data["width"] = set_max_line
                    image_json_data["height"] = set_min_line
                else :
                    width_is_longer = False
                    image_json_data["width"] = set_min_line
                    image_json_data["height"] = set_max_line
                
                new_width = image_json_data["width"]
                new_height = image_json_data["height"]
                
            # 변경된 Image 정보 dump
            with open(file_path, "w", encoding="utf-8") as outfile:
                json.dump(image_json_data, outfile, ensure_ascii=False, indent=4)

            # 이미지 처리 시작
            raw_image_path = f"{raw_folder}{image_path}"
            image_load = cv2.imread(raw_image_path)
            
            # Image를 해상도에 맞게 Resize 진행
            if image_load is not None:
                resized_image = cv2.resize(image_load, (new_width, new_height))
                cv2.imwrite(raw_image_path,resized_image)
            
            else :
                print("이미지가 없거나 경로가 잘못되었습니다.")
                
            # Annotation 정보를 변경해주자.
            anns_path = f"{annotations_folder}{image_id}"
            for root_anns, dirs, anns_files in os.walk(anns_path) :
                for anns_file_name in anns_files:
                    anns_file_path = os.path.join(root_anns, anns_file_name)
                    with open(anns_file_path, 'r') as file_anns:
                        json_data = json.load(file_anns)
                        anns_json_data = copy.copy(json_data)
                        # 각 리스트에서 0 :x, 1 :y, 2 :width, 3 :height
                        anns_json_data["bbox"][0] = anns_json_data["bbox"][0]*d_line
                        anns_json_data["bbox"][1] = anns_json_data["bbox"][1]*d_line
                        anns_json_data["bbox"][2] = anns_json_data["bbox"][2]*d_line
                        anns_json_data["bbox"][3] = anns_json_data["bbox"][3]*d_line
                        # area는 bbox의 면적
                        anns_json_data["area"] = anns_json_data["bbox"][2]*anns_json_data["bbox"][3]
                    
                    # 바뀐 annotation 정보를 dump
                    with open(anns_file_path, "w", encoding="utf-8") as outfile:
                        json.dump(anns_json_data, outfile, ensure_ascii=False, indent=4)
                    


if __name__ == "__main__" :
    # 입력 폴더 및 해상도 설정. Fix here
    dataset_folder = "/home/jy/Desktop/Repo/Data_Curation/dataset_test/dataset/PeopleDataset_else_v1.0.0"
    set_resolution = 640
    
    # Exe
    waffle_dataset_optimizer(dataset_folder, set_resolution)