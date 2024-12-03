import json
import os.path as osp

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_json_file(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)

def concat_str_in_list(list_of_str):
    return ' '.join(list_of_str)


if __name__ == "__main__":
    base_dir = "/run/user/1000/gvfs/dav:host=172.168.47.31,port=15005,ssl=false/AI_data/labeling_data/completed/KTT_C2_Dongtan_HQ/CLIP4Clip_caption_split"
    
    CW_CLASS2CLASSIDX_DICT = read_json_file(osp.join(base_dir,'CW_class2classidx.json'))
    """
    {
        "Box opening": 0,
        "Normal": 1,
        "Snack": 2,
        "Drinking": 3,
        "Clothing change": 4,
        "Shoes change": 5
    }
    """
    
    
    CW_VIDEONAME2CLASSIDX_DICT = read_json_file(osp.join(base_dir,'CW_videoname2classidx.json'))
    SYNTHETHIC_CAPTION_CLIP4CLIP_DICT = read_json_file(osp.join(base_dir,'synthethic_caption_CLIP4CLIP.json'))
    
    caption_dict = {}
    
    for cw_class, class_idx in CW_CLASS2CLASSIDX_DICT.items():
        caption_dict[class_idx] = []
    
    for video_name, class_idx in CW_VIDEONAME2CLASSIDX_DICT.items():
        video_class_idx = CW_VIDEONAME2CLASSIDX_DICT[video_name]
        raw_caption = SYNTHETHIC_CAPTION_CLIP4CLIP_DICT[video_name][0]
        concat_caption = concat_str_in_list(raw_caption)
        
        caption_dict[class_idx].append(concat_caption)
    
    save_json_file(caption_dict, osp.join(base_dir,'caption_dict.json'))