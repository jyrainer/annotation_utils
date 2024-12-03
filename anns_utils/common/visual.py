import json
import cv2
import os


def visual(json_path,src_path,result_folder) :
    label_list = []
    with open(json_path) as f:
        contents = json.load(f)

        # Put label names in label_list
        for label_mark in contents["categories"]:
            label_list.append(label_mark["name"])  # label list (['cls1', 'cls2', ...])

        # Process each image
        for img_contents in contents["images"]:
            img_id = img_contents["id"]
            img_path = src_path + img_contents["file_name"]  # Load image path (coco/images/1.png)
            print(img_path)
            try :
                image_original = cv2.imread(img_path)  # Save original image
                image_result = image_original.copy()  # Output image

                # Process annotations for the current image
                for annotation_contents in contents["annotations"]:
                    if img_id == annotation_contents["image_id"]:
                        cls_index = annotation_contents["category_id"] - 1
                        xy_point = annotation_contents["bbox"]  # x, y, width, height
                        xy_point[0], xy_point[1], xy_point[2], xy_point[3] = int(xy_point[0]), int(xy_point[1]), int(xy_point[2]), int(xy_point[3])
                        # Draw line
                        cv2.rectangle(image_result, (xy_point[0], xy_point[1]), (xy_point[0] + xy_point[2], xy_point[1] + xy_point[3]), (0, 255, 255), 2)

                        # Write Class name
                        text = label_list[cls_index]
                        text_position = (xy_point[0] - 5, xy_point[1] - 5)  # Fix locate
                        #cv2.putText(image_result, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                # Make Result folder as output
                if not os.path.exists(result_folder):
                    os.makedirs(result_folder)
                result_image_path = os.path.join(result_folder, os.path.basename(img_path))
                cv2.imwrite(result_image_path, image_result)  # Save output image

                if not cv2.imwrite(result_image_path, image_result):
                    print("이미지 저장 실패:", result_image_path)
            except :
                print("파일이 없음")

        print("End!")



if __name__ == "__main__" :
    json_path = "/home/jy/Desktop/Repo/Data_Curation/dataset_test/dataset/integrate/coco.json"
    src_path = "/home/jy/Desktop/Repo/Data_Curation/dataset_test/dataset/integrate/image_folder/"
    result_folder = "./result"

    visual(json_path,src_path,result_folder)