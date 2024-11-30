from waffle_utils.file import io, search
import copy
import glob
coco_path = '/home/ljj/Repo/waffle_hub/scripts/coco.json'
cleaning_raw_image = '/home/ljj/ljj/waffle/datasets/nzia_030/draws'
cleaning_raw_image_list = glob.glob(cleaning_raw_image + "/*/**.jpg")

cleaning_glob = []

# 하드코드됨., 이미지 폴더에 따라 변경해야함 TODO
for a in cleaning_raw_image_list:
    cleaning_glob.append(a.split('/')[-2] + '/' + a.split('/')[-1])
cleaning_set = set(cleaning_glob)


coco = io.load_json(coco_path)
cleaned_coco = copy.deepcopy(coco)
del cleaned_coco['annotations']
del cleaned_coco['images']

cleaned_coco_ann_list = []
cleaned_coco_img_list = []
set_img_id = set()

for ori_img in coco['images']:
    if ori_img['file_name'] in cleaning_set:
        cleaned_coco_img_list.append(ori_img)
        set_img_id.add(ori_img['id'])
    else:
        pass

for ori_ann in coco['annotations']:
    if ori_ann['image_id'] in set_img_id:
        cleaned_coco_ann_list.append(ori_ann)
    else:
        pass

print(len(coco['images']))
print(len(cleaned_coco_img_list))
print(len(set_img_id))

cleaned_coco['annotations'] = cleaned_coco_ann_list
cleaned_coco['images'] = cleaned_coco_img_list

io.save_json(cleaned_coco, "/home/ljj/Repo/waffle_hub/scripts/coco_2.json")