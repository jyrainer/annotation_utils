import cv2

from anns_utils.utils.io import load_json, save_json
from glob import glob

CATEGORY_LIST = ["Box opening", "Eating", "Drinking", "Clothes changing", "Shoes changing"]

def get_video_info(video_path):
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)

    return total_frames, fps


def get_annotations_frame_dict(video_path, annotation)->dict:
    total_frame, fps = get_video_info(video_path)
    annotations_frame = {}
    
    for key, value in annotation.items():
        now_frame = int(value[0] * total_frame)
        annotations_frame[key] = [now_frame]
        
    return annotations_frame

def get_class_dict(base_cliped_dir:str, annotations_frame:dict)->dict:
    class_dict = {}
    annotations_dict = {}
    
    for key, value in annotations_frame.items():
        if "S" in key:
            pass
        else:
            s_key = f"S{key[1:]}"
            annotations_dict_key = f"{annotations_frame[s_key][0]} {value[0]}"  # "start end frame"
            annotations_dict[annotations_dict_key] = key
    
    for cliped_category in CATEGORY_LIST:
        target_dir = f"{base_cliped_dir}/{cliped_category}"
        target_video_list = glob(target_dir + "/*.mp4")
        for target_video in target_video_list:
            start_frame = target_video.split(".")[-2].split("_")[-2]
            end_frame = target_video.split(".")[-2].split("_")[-1]
            annotations_dict_key = f"{start_frame} {end_frame}"
            class_key = annotations_dict[annotations_dict_key]
            class_dict[class_key] = cliped_category
            
    return class_dict

if __name__ == "__main__":
    origin_labled_file = "/mnt/nas_192/labeling_data/ToDo/KTT/Coupang_시연데이터/2024-12-03 15-17-01.mov.json"
    base_cliped_dir = "/mnt/nas_192/labeling_data/ToDo/KTT/Coupang_시연데이터/clip"
    origin_labled = load_json(origin_labled_file)
    
    # target_video = origin_labled["path"]
    target_video = "/mnt/nas_192/labeling_data/ToDo/KTT/Coupang_시연데이터/2024-12-03 15-17-01.mov"
    annotations = origin_labled["annotations"]

    annotations_frame = get_annotations_frame_dict(video_path=target_video, annotation=annotations)

    del origin_labled["annotations_frame"]
    origin_labled["annotations_frame"] = annotations_frame
    
    class_dict = get_class_dict(base_cliped_dir,annotations_frame=annotations_frame)
    origin_labled["class"] = class_dict
    
    save_json(origin_labled, f"/mnt/nas_192/labeling_data/ToDo/KTT/Coupang_시연데이터/2024-12-03 15-17-01.mov_newlabel.json")