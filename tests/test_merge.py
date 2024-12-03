from utils.merge_coco import mk_merge_file
import os
import json

def test_noimage():
    # Test 폴더 내의 coco_json 폴더가 입력이 된다.

    categories =    {
                        "categories" :[
                            {
                                "id": 1,
                                "name": "smoke",
                                "supercategory": "smoke"
                            },
                            {
                                "id": 2,
                                "name": "flame",
                                "supercategory": "flame"
                            }
                        ]
                    }
    
    results = mk_merge_file('./coco_json/test1',categories)
    assert len(results["images"]) == 22


    results = mk_merge_file('./coco_json/test2',categories)
    assert len(results["annotations"]) == 4