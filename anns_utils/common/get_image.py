import glob
import os

import cv2

FRAME_INTERVAL = 3


def video_to_image(video_path, frame_interval, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    video_name = video_path.split("/")[-1].replace(".mp4", "")

    cap = cv2.VideoCapture(video_path)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(0, frames, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(f"{output_dir}/{video_name}_framenum_{i:06d}.jpg", frame)
    cap.release()


def get_videos(root_dir: str = "") -> list:
    return glob.glob(f"{root_dir}/**/*.mp4", recursive=True)


if __name__ == "__main__":
    video_path = "/mnt/nas_192/videos/이상행동 CCTV 영상/07.침입(trespass)_clip"
    output_dir = "/mnt/nas_192/videos/이상행동 CCTV 영상/07.침입(trespass)_frame"

    videos = get_videos(video_path)

    for video_path in videos:
        video_to_image(video_path, FRAME_INTERVAL, output_dir)
