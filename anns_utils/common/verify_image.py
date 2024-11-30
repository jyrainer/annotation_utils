import os
import json
import argparse

import numpy as np
from pycocotools.coco import COCO


class VerifyDataset:
    def __init__(self, data_dir,output_dir):
        self.coco = COCO(f"{data_dir}/coco.json")
        self.new_coco_path = f"{output_dir}/new_coco.json"
        self.image_dir = f"{data_dir}/images"
        self.new_coco = self.coco.dataset
        self.new_imgs = []
        self.new_anns = []
    
    def validate(self):
        '''
        Process : -> ->
        '''
        self._check_no_anno_image()
    
    def _check_no_anno_image(self):
        '''
        이미지의 존재 여부와 이미지에 해당하는 annotation 정보를 확인한다.
        모든 validate 과정에 대해 통과한 images, annotations에 대해서만 새로 coco.json을 저장한다.
        다음은 검증 목록이다.

            1. images-file_path가 존재하지만 실제 이미지 파일이 존재하지 않는 경우는 False
            2. 각 이미지에 매칭되는 annotations 정보를 얻어 이미지는 존재하지만(? 이미지는 존재하지만?), annotation(label) 정보가 존재하지 않는 경우 False
            3. Annotation 정보에서 중복되는 label을 제거하고, annotation의 coordinate 좌표 정보가 image width, height보다 클 경우 False
        
        모든 검증을 통과할 경우, annotations 및 images 정보가 json파일에 dump된다.
        '''
        imgs = self.coco.imgs
        for img in imgs.values():
            file_path = f"{self.image_dir}/{img['file_name']}"
            if os.path.isfile(file_path): # 1. Check Image File

                anns_ids = self.coco.getAnnIds(imgIds=img['id'])
                anns = self.coco.loadAnns(anns_ids)

                if len(anns) == 0:   # 2. Check Annotation info
                    print("No Annotations Image")
                else:
                    lb = np.array([anno['bbox'] for anno in anns])
                    _, i = np.unique(lb, axis=0, return_index=True)
                    lb = lb[i] # 3.1 Remove duplicate
                    
                    width_check = (lb[:, 0] + lb[:, 2]) <= img['width']
                    height_check = (lb[:, 1] + lb[:, 3]) <= img['height']
                    # width_check = np.argwhere((lb[:, 0] + lb[:, 2]) < img['width']).flatten()
                    # height_check = np.argwhere((lb[:, 1] + lb[:, 3]) < img['height']).flatten()
                    if (width_check.all() and height_check.all()):      # 3.2 Check range of bbox in image
                        self.new_imgs.append(img)
                        self.new_anns += (np.array(anns)[i].tolist())
                    else:
                        print(f"Plz Check, {lb[width_check]} or {lb[height_check]}")
            else:
                print(f"Image Id exist. but No Image file {file_path}")
    

        self.new_coco['images'] = self.new_imgs
        self.new_coco['annotations'] = self.new_anns

        self.coco_save()

    def coco_save(self):
        """
        new_coco의 내용을 new_coco_path 위치에 json 형식으로 저장
        """
        print("New coco json Save !!")
        with open(f"{self.new_coco_path}", "w", encoding="utf-8") as outfile:
            json.dump(self.new_coco, outfile, ensure_ascii=False)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='coco train & val Merge.')
    parser.add_argument('--data_dir', type=str, default="/home/jy/Desktop/Repo/Data_Curation/workspase", help='Your Dataset Directory.')
    parser.add_argument('--output_dir', type=str, default="/home/jy/Desktop/Repo/Data_Curation/workspase/result", help='New Dataset Directory.')
    args = parser.parse_args()

    V = VerifyDataset(args.data_dir,args.output_dir)
    V.validate()
