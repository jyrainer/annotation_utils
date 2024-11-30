import xml.etree.ElementTree as ET
import shutil
from glob import glob

MAJOR_CATEGORY = {
    "01.폭행(assult)_clip" : "Violence",
    "02.싸움(fight)_clip" : "Fight",
    "05.실신(swoon)_clip" : "Swoon"
}

MINOR_CATEGORY = {
    "Violence": {
        "Violence" : ['piercing', 'pulling', 'kicking', 'threaten', 'throwing', 'punching', 'pushing'],
        "Falldown" : ['falldown']
    },
    "Fight": {
        "Violence" : ['piercing', 'pulling', 'kicking', 'threaten', 'throwing', 'punching', 'pushing'],
        "Falldown" : ['falldown']
    },
    "Falldown": {
        "Falldown" : ['falldown']
    }
}

def get_dir_list(base_dir: str):
    """해당 경로 내에 디렉터리 path를 리턴한다."""
    return glob(base_dir + "/*")

def get_file_list(base_dir: str, extension: str):
    """extension 으로 끝나는 파일들을 리턴한다."""
    return glob(base_dir + "/**/*." + extension, recursive=True)

def extract_category(category: str, xml_file_list: list[str]):
    action_set = set()
    for file_path in xml_file_list:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for object_elem in root.findall('object'):
            for action_elem in object_elem.findall('action'):
                if action_elem.find('actionname') is not None:
                    action_set.add(action_elem.find('actionname').text)

    print(f"Category: {category.split('/')[-1]}, Action Set: {action_set}")

def move_video_files():
    pass

if __name__ == '__main__':
    ## 1. extract category
    base_dir = "/mnt/nas_192/videos/이상행동 CCTV 영상"

    category_dir = get_dir_list(base_dir)
    
    for category in category_dir:
        xml_file_list = get_file_list(category, "xml")
        extract_category(category, xml_file_list)

    ###########################
    
    ### 2. move video files

    move_video_files()