from utils.check_noimage_coco import rm_label_noimage
import os
import json

def test_noimage():
    # 임의의 데이터
    coco_data1 = {
        "images": [
            {
                "id": 121917,
                "file_name": "fire_resize/S3-N1427MF01643.jpg",
                "height": 720,
                "width": 1280
            },
            {
                "id": 130000,
                "file_name": "fire_resize/S3-N1427MF01643.jpg",
                "height": 720,
                "width": 1280
            },
            {
                "id": 150000,
                "file_name": "S3-N0837MF05130.jpg",
                "height": 720,
                "width": 1280
            }
        ],
        "annotations": [
            {
                "id": 1,
                "image_id": 121917,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            },
            {
                "id": 1,
                "image_id": 130000,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    1110
                ]
            },
            {
                "id": 2,
                "image_id": 150000,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    1110
                ]
            }
        ]
    }


    results = rm_label_noimage(coco_data1)
    assert len(results) == 1


    coco_data2 = {
        "images": [
            {
                "id": 121917,
                "file_name": "fire_resize/S3-N1427MF01643.jpg",
                "height": 720,
                "width": 1280
            },
            {
                "id": 130000,
                "file_name": "fire_resize/S3-N1427MF01643.jpg",
                "height": 720,
                "width": 1280
            },
            {
                "id": 150000,
                "file_name": "S3-N0837MF05130.jpg",
                "height": 720,
                "width": 1280
            }
        ],
        "annotations": [
            {
                "id": 1,
                "image_id": 121917,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            },
            {
                "id": 1,
                "image_id": 130000,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    1110
                ]
            },
            {
                "id": 2,
                "image_id": 150500,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    1110
                ]
            }
        ]
    }

    results = rm_label_noimage(coco_data2)
    assert len(results) == 0