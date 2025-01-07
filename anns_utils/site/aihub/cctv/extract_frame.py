import glob
import os
import xml.etree.ElementTree as ET

import cv2
import tqdm

FPS = 29.970030
FRAME_INTERVAL = 3
SHAPE = (1920, 1080)


def get_videos(root_dir: str = "") -> list:
    return glob.glob(f"{root_dir}/**/*.mp4", recursive=True)


def convert_time_to_seconds(time_str: str) -> float:
    hours, minutes, seconds = map(float, time_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def get_event_frame(
    video_path: str,
    before_margin: int = 15,
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
    xml_path = video_path.replace(".mp4", ".xml")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    starttime = root.find("event/starttime").text
    duration = root.find("event/duration").text

    frames = int(root.find("header/frames").text)

    starttime_seconds = convert_time_to_seconds(starttime)
    duration_seconds = convert_time_to_seconds(duration)

    start_frame = int(starttime_seconds * FPS)
    end_frame = int((starttime_seconds + duration_seconds) * FPS)

    before_frame = int(max(0, start_frame - before_margin * FPS))
    after_frame = int(min(frames - 1, end_frame + after_margin * FPS))

    return [before_frame, after_frame]


def get_image_file(video_path, frame_interval, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    video_name = video_path.split("/")[-1].replace(".mp4", "")

    cap = cv2.VideoCapture(video_path)

    event_frame = get_event_frame(video_path)

    for i in range(event_frame[0], event_frame[1], frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        frame = cv2.resize(frame, SHAPE)
        if not ret:
            break
        cv2.imwrite(f"{output_dir}/{video_name}_framenum_{i:06d}.jpg", frame)
    cap.release()


if __name__ == "__main__":
    videos = get_videos(root_dir="/mnt/nas_192/videos/이상행동 CCTV 영상/07.침입(trespass)")
    for video in tqdm.tqdm(videos):
        get_image_file(
            video,
            frame_interval=FRAME_INTERVAL,
            output_dir="/mnt/nas_192/videos/이상행동 CCTV 영상/07.침입(trespass)_frame",
        )
