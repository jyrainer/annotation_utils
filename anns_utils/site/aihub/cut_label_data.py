import glob
import os

from pathlib import Path

def cut_label(img_path,label_path):
    """
    AI_hub에서 화재씬 데이터를 처리할 때 사용한다.
    각 이미지마다 1:1로 라벨데이터가 들어있는 파일이 존재한다.
    53만개의 파일이 모두 필요하진 않으므로, img_path에 존재하는 이미지에 매칭되는 라벨 데이터를 제외하고 모든 라벨데이터를 제거한다.

    args:
        folder 1 : img_path including images
        folder 2 : label_path including label_data files

    returns:
        필요없는 라벨 데이터 제거
    """
    images = glob.glob(img_path+"/*")
    labels = glob.glob(label_path+"/*")
    print("첫 라벨 데이터 개수 :", len(labels))
    print("첫 이미지 데이터 개수 :", len(images))

    a = 0   # 삭제된 라벨 수
    b = 0   # 남은 라벨 수
    for label_path in labels:
        filename = Path(label_path).stem
        check_name = f"{img_path}/{filename}.jpg"
        if check_name not in images:
            a+=1
            os.remove(label_path)
        else:
            b+=1
            # print(label_path)

    

    print("제거된 라벨 데이터 수 :", a, "남은 라벨 데이터 수 :", b)



if __name__ == "__main__" :
    img_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/result_200'     # Fix me
    label_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/label_200'    # Fix me
    cut_label(img_path,label_path)