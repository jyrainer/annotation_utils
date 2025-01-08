import glob
import os
import xml.etree.ElementTree as ET

import cv2
import tqdm

FPS = 30
FRAME_INTERVAL = 3
SHAPE = (1920, 1080)


def get_videos(root_dir: str = "") -> list:
    return glob.glob(f"{root_dir}/**/*.mp4", recursive=True)


def convert_time_to_seconds(time_str: str) -> float:
    hours, minutes, seconds = map(float, time_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def get_event_frame(
    video_path: str,
    before_margin: int = 8,
    after_margin: int = 4,
) -> list[int, int]:
    """_summary_

    Args:
        video_path (str): _description_
        before_margin (int, optional): _description_. Defaults to 15.
        after_margin (int, optional): _description_. Defaults to 5.

    Returns:
        list[int, int]: start frame, end frame
    """
    xml_path = video_path.replace(".mp4", ".xml")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    starttime = root.find("event/starttime").text
    duration = root.find("event/duration").text

    frames = int(root.find("header/frames").text)

    event = str(root.find("object/action/actionname").text)
    starttime_seconds = convert_time_to_seconds(starttime)
    duration_seconds = convert_time_to_seconds(duration)

    start_frame = int(starttime_seconds * FPS)
    end_frame = int((starttime_seconds + duration_seconds) * FPS)

    before_frame = int(max(0, start_frame - before_margin * FPS))
    after_frame = int(min(frames - 1, end_frame + after_margin * FPS))

    return [before_frame, after_frame], event


def get_image_file(video_path, frame_interval, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    video_name = video_path.split("/")[-1].replace(".mp4", "")

    cap = cv2.VideoCapture(video_path)

    event_frame, event_name = get_event_frame(video_path)

    for i in range(event_frame[0], event_frame[1], frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        frame = cv2.resize(frame, SHAPE)
        if not ret:
            break
        cv2.imwrite(f"{output_dir}/{video_name}_framenum_{i:06d}.jpg", frame)
    cap.release()


# 비디오 클립을 저장하는 함수
def save_video_clips(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    video_name = os.path.basename(video_path).replace(".mp4", "")

    # 비디오 캡처 객체 생성
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return

    event_frame, event_name = get_event_frame(video_path)

    ### 하드코딩
    if int(video_name.split("_")[0].split("-")[0]) >= 151:
        pass
    else:
        print(f"Video: {video_name}")
        return
    if event_name == "climbwall":
        pass
    else:
        print(f"Event: {event_name}, Video: {video_name}")
        return
    # 저장할 비디오 형식 설정
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_path = os.path.join(output_dir, f"{video_name}_clip.mp4")
    video_clip = cv2.VideoWriter(output_path, fourcc, FPS, SHAPE)

    # 프레임 간격에 따라 프레임 저장
    for frame_idx in range(event_frame[0], event_frame[1]):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        frame = cv2.resize(frame, SHAPE)
        if not ret:
            print(f"Warning: Could not read frame at index {frame_idx}")
            break

        video_clip.write(frame)

    # 리소스 해제
    video_clip.release()
    cap.release()
    print(f"Video clip saved to {output_path}")


if __name__ == "__main__":
    videos = get_videos(root_dir="/mnt/nas_192/videos/이상행동 CCTV 영상/07.침입(trespass)")
    for video in tqdm.tqdm(videos):
        save_video_clips(video, "/mnt/nas_192/videos/이상행동 CCTV 영상/07.침입(trespass)_clip")
