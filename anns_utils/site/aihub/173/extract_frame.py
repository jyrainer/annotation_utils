import glob
import os
import json

import cv2
import tqdm

FPS = 3
FRAME_INTERVAL = 1
SHAPE = (1920, 1080)

LABEL_POSTFIX = "라벨링데이터"
VIDEO_POSTFIX = "원천데이터"

def get_videos(root_dir: str = "") -> list:
    return glob.glob(f"{root_dir}/**/*.mp4", recursive=True)


def convert_time_to_seconds(time_str: str) -> float:
    hours, minutes, seconds = map(float, time_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def parse_event_json(json_path: str) -> dict:
    """173의 라벨파일에만 적용됨"""
    result = []
    with open(json_path, "r") as f:
        json_data = json.load(f)
    
    events = json_data["events"]
    
    for event in events:
        result.append([event["ev_start_frame"], event["ev_end_frame"]])

    return result

def get_event_frame(
    video_path: str,
    before_margin: int = 5,
    after_margin: int = 5,
) -> list[int, int]:
    """_summary_

    Args:
        video_path (str): _description_
        before_margin (int, optional): _description_. Defaults to 15.
        after_margin (int, optional): _description_. Defaults to 5.

    Returns:
        list[int, int]: start frame, end frame
    """
    events = parse_event_json(video_path.replace(VIDEO_POSTFIX, LABEL_POSTFIX).replace(".mp4", ".json").replace("TS", "TL"))
    total_frame = int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FRAME_COUNT))
    result = []
    for event in events:
        start_frame = event[0]
        end_frame = event[1]
        before_frame = int(max(0, start_frame - before_margin * FPS))
        after_frame = int(min(end_frame + after_margin * FPS, total_frame))
        result.append([before_frame, after_frame])
    
    return result

    

def get_image_file(video_path, frame_interval, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    video_name = video_path.split("/")[-1].replace(".mp4", "")

    cap = cv2.VideoCapture(video_path)

    event_frames = get_event_frame(video_path)

    for cnt, event_frame in enumerate(event_frames):
        for i in range(event_frame[0], event_frame[1], frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            frame = cv2.resize(frame, SHAPE)
            if not ret:
                break
            cv2.imwrite(f"{output_dir}/{video_name}_eventnum_{cnt}_framenum_{i:06d}.jpg", frame)

    cap.release()


if __name__ == "__main__":
    videos = get_videos(root_dir="/mnt/nas_192/videos/new_dataset/173.공원_주요시설_및_불법행위_감시_CCTV_영상_데이터/01.데이터/1.Training/원천데이터/TS_행위(불법행위)데이터2.zip_extracted/1.불법행위/4.월담행위")
    for video in tqdm.tqdm(videos):
        get_image_file(video, FRAME_INTERVAL, "/mnt/nas_192/videos/KTT_Yonsei/173.공원_주요시설_및_불법행위_감시_CCTV_영상_데이터_01.데이터_1.Training_원천데이터_TS_행위(불법행위)데이터2.zip_extracted_1.불법행위_4.월담행위_frame")
