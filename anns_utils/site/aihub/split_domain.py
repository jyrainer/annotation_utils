import shutil
import os

# 하나의 폴더 대상으로 도메인 별 n개가 되도록 이미지 나누기
def divid_cal(n, folder):
    """
    현재 aihub의 화재씬에서는 한 도메인(비슷한 배경)에 프레임 단위의 이미지들이 존재하며, 많으면 한 도메인에 5000장 이상이 존재한다.
    이는 overfitting을 유발할 수 있으므로 다음과 같은 방식을 제안한다.
        1. 화재씬에서 도메인은 이미지 이름의 앞 8자리가 동일할 시 같은 도메인이다. 따라서 앞 8자리가 다르면 도메인이 다르다고 볼 수 있다.
        2. 한 도메인 당 200, 500장씩 리스트에서 뽑아와서 학습 대상 데이터로 선정한다.
        3. divid_cal에서 return되는 이미지 경로에 대한 list를 excute_divid 함수에서 인자로 받아 실제로 이미지를 던져준다.
    한 도메인 당 200, 500장씩 나누어 Exp1, Exp2로 학습하여 결과를 확인하고 분석을 하는 것이 목적이다. (같은 도메인 조건에 이미지 개수에 따라 유의미한 변화를 일으키는가?)

    input 1 : 도메인별 희망 결과 이미지 개수
    input 2 : 실행 대상 폴더
    """
    domain_list = []    # 각 도메인의 이미지는 이 리스트에 모두 담긴다.
    result_list = []    # 실제로 보낼 이미지들은 이 리스트에 담긴다.

    seen_id = set()     # seen_id에서는 도메인 이름을 넣는다. 도메인을 구분할 수 있다.
    a = 1               # a는 각 도메인별 파일 개수를 세린다.
    b = 0               # b는 총 도메인 개수를 세린다.
    d = 0               # 어떻게 나눌 것인가? d = 도메인별 이미지개수 / n
    all_img = 0         # 이미지 총 개수 세림
    for folder_name, _, filenames in os.walk(folder):           # os.walk로 파일 목록을 받음
        for filename in sorted(filenames):                      # filenames(폴더내 파일)을 오름차순 정렬(sorted)한다.
            domain_name = filename[:8]                            # 이미지 파일 앞 8글자가 도메인 정체성을 가짐
            if domain_name not in seen_id :                       # 만약 seen_id set에 저장되지 않았다면
                seen_id.add(domain_name)                          # seen_id에 도메인 추가
                if len(seen_id) == 1 :                          # seen_id가 1일땐 맨 첫번째 도메인을 감지한 것이다. 이하 연산은 생략하고 넘어간다.
                    print("도메인 이름 :", domain_name)               # 도메인 이름 출력
                    b += 1
                    continue
                print("도메인 이름 :", domain_name)               # 도메인 이름 출력
                b += 1                                          # b는 도메인 개수를 세린다.
                #print("해당 도메인의 이미지 총 개수 :", a)           # a는 도메인 당 이미지 개수이며, domain_list의 최대 인덱스를 가리킨다.(a-1)
                d = int(a/n)
                const_d = d
                # return값 저장하는 부분
                if a-1 <= n :                               # 만약 n보다 도메인별이미지가 적다면
                    for append_list in domain_list :
                        result_list.append(append_list)     # 해당 도메인의 모든 이미지 리스트를 연결
                else :
                    while ( d < a-1 ) :
                        result_list.append(domain_list[d])
                        d += const_d
                domain_list.clear()                 # 연산 종료후 도메인 초기화
                all_img += a                        # 총 이미지 개수
                a = 1
            else:
                domain_list.append(filename)
                a += 1

        # 마지막 짜투리 도메인 처리
        d = int(a/n)
        const_d = d
        # return값 저장하는 부분
        if a-1 <= n :                             # 만약 n보다 도메인별이미지가 적다면
            for append_list in domain_list :
                result_list.append(append_list)     # 해당 도메인의 모든 이미지 리스트를 연결
        else :
            while ( d < a-1 ) :
                result_list.append(domain_list[d])
                d += const_d
        #print("마지막 도메인의 이미지 총 개수 :", a)           # a는 도메인 당 이미지 개수이며, domain_list의 최대 인덱스를 가리킨다.(a-1)
        all_img += a

    print("이미지 전체 개수 :", all_img)
    print("총 도메인 개수 :", b)
    return result_list


# 리스트로 받은 이미지들을 result 폴더에 던지는 함수
def excute_divid(list, img_path, result_path):
    """
    divid_cal에서 return값을 받을 수 있다. 해당되는 리스트들을 뽑아 result_path에 이미지를 던질 수 있다.
    input 1 : 대상 이미지 리스트
    input 2 : 대상 폴더
    input 3 : 결과 저장 폴더
    """
    # list개수만큼 반복
    for img_list in list :
        src = os.path.join(img_path, img_list)      # img_path는 이미지의 절대 경로를 알림
        destination_path = os.path.join(result_path, img_list)  # 목적 경로
        shutil.copy(src, destination_path)         # shutil로 이미지 복 붙
        print("파일 복사 완료:", destination_path)         # 저장된 경로 print

if __name__ == "__main__" :
    # To-do

    # 도메인당 약 200장이 목표일 경우 예시. 200장을 맞추기 위해 나눗셈 연산 시 200장을 딱 맞추기 보단 근접하게 맞춘다.
    n = 200
    img_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/[원천]화재씬_'
    result_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/result_200'
    result_list = divid_cal(n, img_path)                # Function 1
    print(len(result_list))
    excute_divid(result_list, img_path, result_path)    # Function 2

    # # 메크로
    # i = 1
    # for i in range(1,14) :
    #     img_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/[원천]화재씬_'+str(i)
    #     result_path = '/media/jy/f3a9e7bd-8096-48b8-a5ca-d5aa29c94151/33download/Fire_of_all/workspase/result_200'
    #     result_list = divid_cal(n, img_path)                # Function 1
    #     print(len(result_list))
    #     excute_divid(result_list, img_path, result_path)    # Function 2
    #     i += 1