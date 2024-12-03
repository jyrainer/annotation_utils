from utils.check_outbbox_coco import remove_out_bbox


def test_outbbox():
    
    # case1. 정상적인 경우, 안바뀜
    test_data = {
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
                    100
                ]
            }
        ],
    }
    results = remove_out_bbox(test_data)
    assert len(results) == 2
    
    
    # case2. width가 넘어갈 때
    test_data = {
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
                    81,
                    1281,
                    100
                ]
            }
        ],
    }
    results = remove_out_bbox(test_data)
    print(results)
    assert len(results) == 1
    
    # case3. height가 넘어갈 때
    test_data = {
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
                    81,
                    100,
                    650
                ]
            }
        ],
    }
    results = remove_out_bbox(test_data)
    print(results)
    assert len(results) == 1