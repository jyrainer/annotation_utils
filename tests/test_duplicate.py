from utils.check_duplicate_label_coco import remove_dup_label


def test_remove_duplicate_label():
    
    # case1. image_id가 같으나 bbox정보가 다를 경우 제거하면 안되므로 annotation 개수가 2가 나와야함
    test_data = {
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            },
            {
                "id": 2,
                "image_id": 1,
                "category_id": 2,
                "bbox": [
                    0,
                    0,
                    110,
                    110
                ]
            }
        ]
    }

    results = remove_dup_label(test_data["annotations"])

    assert len(results) == 2

    # case2. image_id가 같고 bbox정보가 같으며 클래스까지 같으면 제거된 뒤 annotation 개수가 1개가 나와야함
    test_data2 = {
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            },
            {
                "id": 2,
                "image_id": 1,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            }
        ]
    }
    results = remove_dup_label(test_data2["annotations"])

    assert len(results) == 1
    
    # case3. image_id가 같고 bbox정보가 같으나, category_id가 다를 때, 그대로 2개가 나와야함
    test_data3 = {
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            },
            {
                "id": 2,
                "image_id": 1,
                "category_id": 2,
                "bbox": [
                    0,
                    0,
                    100,
                    100
                ]
            }
        ]
    }
    results = remove_dup_label(test_data3["annotations"])
    assert len(results) == 2