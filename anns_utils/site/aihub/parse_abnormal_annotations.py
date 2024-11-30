import xml.etree.ElementTree as ET
from glob import glob

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

if __name__ == '__main__':
    base_dir = "/mnt/nas_192/videos/이상행동 CCTV 영상"
    raw_category_dir = glob(base_dir + "/*")
    category_dir = [i for i in raw_category_dir if i.split("/")[-1] != "_clip"]
    
    for category in category_dir:
        xml_file_list = glob(category + "/**/*.xml", recursive=True)
        extract_category(category, xml_file_list)
