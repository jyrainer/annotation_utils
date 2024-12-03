# annotation_utils
어노테이션을 파싱하는 코드 모음입니다

<!-- # Data_Utils
Dataset Utils는 임시로 만든 Repository이며, 각종 데이터셋에 대해 Merge, Curation, Validation, Convert 등에 대한 기능을 담은 저장소입니다.
추후에 waffle에 각 기능을 추가할 예정.

---
## 1. Verify Labels and Images for Coco annotations format

```
$ cd utils
$ python verify_image.py --data_dir={your_input} --output_dir={your_output}
```

### § 중복 라벨링 제거
- annotation의 image_id가 중복되는 경우에 한 이미지에 여러 개의 bbox 정보가 존재합니다.
- 이 때, 같은 내용의 bbox 정보가 있을 때, bbox정보를 하나만 남깁니다.

### § bbox 인덱스 관리
- 기존 입력 이미지의 해상도를 초과할 경우 해당 label을 없애줍니다.

### § 존재하지 않는 이미지일 경우 라벨 제거
- annotation에서 주어지는 이미지 경로를 추적하여 존재하지 않을 경우 label을 없애줍니다.
- 이미지 경로에서 label이 없을 경우 json에서 file_path를 없애줍니다.
---

## Dataset Convert
### SuperbAI Suite to COCO
```
$ cd utils
$ python superb_to_coco.py
```
현재 데이터셋이 산재되어 있어 각 데이터셋을 SuperbAI suite로부터 다운로드 받아 coco format으로 변환한다.

---
## Visualize bbox
```
$ cd utils
$ python visual.py
```
- 라벨과 이미지 폴더를 지정시, bbox를 친 뒤, 해당 이미지를 result 폴더에 저장한다.

---
## Label_Merge
### 1. coco 파일 합병
```
$ cd utils
$ python merge_coco.py
```
- coco.json 형태의 파일들이 들어있는 폴더를 입력으로 주면, 하나의 coco.json으로 만들게 된다.
- 단, categories (class 지정 관련) 는 사용자가 직접 수정하는 것으로 한다.
---
## Image_integrate
### 1. 이미지 경로 통합
```
$ cd utils
$ python integrate_image.py
```
- 여러 폴더나 여기저기 image 가 퍼져있을 때, images라는 폴더 한 곳에 이미지를 모은다.
- coco.json 에 적혀있는 file_path의 경우도 수정이 필요하다. 이 때 기존 폴더는 images에서 meta_data라는 key에 str형태로 저장해둔다.
- 이미지 이름은 000000.* 부터 차례대로 스트링 숫자 형태로 이름을 가지며, 시작 번호를 지정할 수 있다.

---
## COCO_Slice
```
$ cd utils
$ python slice.py
```
- 이미지 경로 및 coco.json 경로를 입력해주면, 해당 이미지를 4등분 및 센터 총 5개의 이미지를 생성한다..
- 이때 그에 따라 라벨 정보가 바뀌며, 이미지에 객체가 걸쳐있거나 없을 경우 이미지를 생성하지 않는다.
---
## Waffle_letter_boxing
```
$ cd utils
$ python waffle_letter_boxing.py
```
- Waffle dataset 폴더를 입력으로 둘 때, 이미지 사이즈 및 라벨정보를 변경하여, 데이터셋 archive 시 데이터 용량에 대한 이점을 제공한다.
- 한 변의 최대 길이를 입력(resolution)으로 두고, 나머지 변은 줄어들거나 늘어난 ratio에 비례해 재조정된다.
---
## ★AI_Hub

## Fire Scene관련
### 1. aihub_to_coco
- 화재씬 데이터를 coco annotation format으로 바꾼다.
### 2. cut_label_data
- raw한 라벨 데이터셋은 이미지와 1:1매칭되므로 필요없는 라벨 데이터를 삭제한다.
### 3. split_domain
- 한 도메인에 지나치게 많은 이미지가 존재하므로, 한 도메인당 최대로 가질 수 있는 이미지 장수를 설정하여 split할 수 있다.
---
## 교통정리 시내도로 관련
### 1. aihub_traffic
- aihub의 시내도로 데이터에서 coco annotations로 바꾸기 위한 작업을 할 수 있다.
---
## 교통정리 고속도로 관련
### 1. xml_2_coco
- aihub의 고속도로 데이터의 라벨링 데이터는 커스텀의 xml 포맷을 가지고 있다. 따라서 coco로 변환해주어야 한다.
- .xml이 들어있는 폴더와 클래스 정보를 가진 categories를 지정해주어 함수를 실행할 수 있다. -->