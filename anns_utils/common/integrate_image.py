import os
import argparse
import json

from pathlib import Path
import shutil


class IntergrateCOCO:

    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.start_num = 0


    def create_result_folder(self):
        '''
        # 폴더 생성 함수
        '''
        if not os.path.isdir(self.output_dir):
            # os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(f"{self.output_dir}/images")
        else:
            
            raise "Exist Save Directory, Plz Check Directory Path"

    def integrate_image(self):
        """
        이미지를 한곳에 통합하는 함수, json도 수정됨
        이 함수는 coco.json을 입력으로 하여 path 등의 정보를 받는다.
        이미지들은 images라는 폴더의 하위에 모든 이미지들을 두고, coco.json은 그 path에 알맞게 수정되도록 한다. 
        결과적으로 이미지를 한 곳에 모은 images라는 폴더와 new_coco.json 파일을 result 폴더에 생성하게 된다.
        이미지 이름은 총 6자리이며, 0을 꽉채운 숫자 나열이다.
        args:
            1. dict : coco json form
            2. folder : root folder including images defined as coco.json
            3. integer : start number of image name ( start_num ≤ 999999 )

        returns:
            dict : coco json form        

        folder tree ex)
        [before]
            folder   ─┬──*coco.json 
                    │         
                    └──**root_img───┬  image_path1  ┬  q.jpg
                                    │               └  w.jpg
                                    │
                                    ├  image_path2  ┬ adsds.jpg 
                                    │   ...         ...
        (* : input1, ** : input2 )
        
        [after]
            result(현재 작업 디렉토리)  ────┬  coco.json(지정가능)
                                        └  images   ┬  000000.jpg
                                                    ├  000001.jpg
                                                    ├  000002.jpg
                                                    ├  000003.jpg                
                                                    │ ... 
        """
        with open(f"{self.input_dir}/coco.json", 'r') as file:
            coco_data = json.load(file)                         # coco_data는 json파일의 모든 내용을 담는다.
            for images_info in coco_data["images"] :            # images의 개수만큼 반복. 개수만큼 이미지가 존재하게 된다.
                image_path = images_info["file_name"]           # image_path는 이미지 경로를 포함한 이미지 이름이나, 경로를 제외한 이미지 이름을 가진다. 이미지 이름만 있으면 된다
                images_info["meta_path"] = str(image_path)       # images내에 키 값으로 meta_path를 추가하며 value는 이미지 상대경로를 가지게 된다.
                image_name = Path(image_path).parts[-1]                # 이미지 이름만 image_name에 추출
                image_extension = image_name[-4:]               # 파일 확장자
                
                after_image_path = str(self.start_num).zfill(6)+image_extension  # image의 이름은 다음과 같이 통일한다. ex) 000000.jpg, 000001.png ... 
                                                                    # images_path는 경로를 제외한 숫자로 이루어진 이미지 이름으로 남게 된다.

                # 이미지 images라는 폴더로 이동
                src_path = f"/Users/ljj/workspace/dataset/{image_path}"
                dst_path = f"{self.output_dir}/images/{after_image_path}"
                try :
                    shutil.copyfile(src_path, dst_path)
                    images_info["file_name"] = after_image_path             # 기존 file_name 교체
                    self.start_num += 1                                                  # image 카운트
                except :
                    print("해당 이미지가 존재하지 않습니다 : ", src_path)

        with open(f"{self.output_dir}/coco.json", "w", encoding="utf-8") as outfile:
            json.dump(coco_data, outfile, ensure_ascii=False)


if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='coco train & val Merge.')
    parser.add_argument('--input_dir', type=str, default="/Users/ljj/workspace/dataset/KISA-person_v1", help='Your Dataset (COCO Format).')
    parser.add_argument('--output_dir', type=str, default="/Users/ljj/workspace/dataset/KISA-person_v1_output_val", help='Save Your New Coco Directory.')
    args = parser.parse_args()

    run = IntergrateCOCO(args.input_dir, args.output_dir)

    run.create_result_folder()
    run.integrate_image()