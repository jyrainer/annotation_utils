import os
import re
import subprocess


def get_target_folder_list(
    raw_video_root_path: str,
    start_time_stemp: str,
    end_time_stemp: str,
    max_video_duration: int,
) -> list:
    """
    Get the target folder list based on the start and end time stamps.
    """
    target_folder_list = []
    start_time_stemp = int(start_time_stemp)
    end_time_stemp = int(end_time_stemp)

    for folder in os.listdir(raw_video_root_path):
        folder_path = os.path.join(raw_video_root_path, folder)
        if os.path.isdir(folder_path):
            start_time = int(folder.split("-")[0])
            end_time = int(folder.split("-")[1])
            cond1 = start_time >= start_time_stemp and end_time <= end_time_stemp
            clip_folders = os.path.join(folder_path, os.listdir(folder_path)[0])
            num_clip_folders = len(os.listdir(clip_folders)) - 1
            cond2 = num_clip_folders <= max_video_duration

            if cond1 and cond2:
                target_folder_list.append(folder_path)
                # print(f"num_clip_folders: {num_clip_folders}")

    return target_folder_list


def get_uuid_folder(ts_folder_path: str) -> str:
    """
    Given a ts_folder_path, find and return the UUID folder inside it.
    """
    # Regular expression to match a valid UUID format
    uuid_pattern = re.compile(r"^[a-f0-9\-]{36}$")

    # Get the list of files and folders inside ts_folder_path
    contents = os.listdir(ts_folder_path)

    # Loop through the contents and find the folder that matches the UUID pattern
    for content in contents:
        if uuid_pattern.match(content):  # Check if it matches the UUID pattern
            return content

    return None  # Return None if no valid UUID folder is found


def save_video(target_folder_list: list, save_path: str) -> None:
    """
    Save the video clips from the target folders into a single MP4 file.
    Each folder contains multiple .ts video parts that need to be concatenated.
    """
    os.makedirs(save_path, exist_ok=True)  # Create the save path if it doesn't exist

    # Traverse through each folder in the target_folder_list
    for folder_path in target_folder_list:
        video_files = []
        # Get the subfolder (UUID folder) inside each main folder
        place = os.listdir(folder_path)[0]
        # os.makedirs(os.path.join(save_path, place), exist_ok=True)  # Create the subfolder in save_path
        uuid_folder = os.path.join(folder_path, place)

        # Find all .ts folders within the uuid folder and sort them
        ts_folders = [f for f in os.listdir(uuid_folder) if f.endswith(".ts")]
        ts_folders.sort()  # Sort the .ts folders in ascending order

        # For each .ts folder, find the 'part.1' file and add it to the list
        for ts_folder in ts_folders:
            ts_folder_path = os.path.join(uuid_folder, ts_folder)
            ts_uuid_target_folder = get_uuid_folder(ts_folder_path)
            ts_uuid_folder = os.path.join(ts_folder_path, ts_uuid_target_folder)
            part_file = os.path.join(ts_uuid_folder, "part.1")

            if os.path.exists(part_file):
                video_files.append(part_file)

        # Now, video_files contains the list of all .ts files to concatenate
        # Create a text file with the list of .ts files in the format required by ffmpeg
        concat_list_file = os.path.join(save_path, "concat_list.txt")
        with open(concat_list_file, "w") as f:
            for video in video_files:
                f.write(f"file '{video}'\n")

        # Define the output file path
        folder_name = folder_path.split("/")[-1]
        file_name = f"{folder_name}.mp4"
        output_file = os.path.join(save_path, file_name)

        # Use ffmpeg to concatenate the video files
        command = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list_file,
            "-c:v",
            "libx264",  # Re-encode video with H.264 codec
            "-c:a",
            "aac",  # Re-encode audio with AAC codec
            "-strict",
            "experimental",  # Allow experimental codecs (for AAC)
            "-preset",
            "fast",  # Use a faster encoding preset (you can also use 'medium' or 'slow')
            output_file,
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Video saved successfully to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error while concatenating videos: {e}")


if __name__ == "__main__":
    raw_video_root_path = "/media/gpuadmin/One Touch/ktt_14th_clip"
    start_time_stemp = "1747700439211"  # 1747700439.211
    end_time_stemp = "1747817452321"  # 1747817452.321
    # end_time_stemp = "1747701274521" # 1747817452.321 TEST
    max_video_duration = 15
    result_path = "/media/gpuadmin/One Touch/ktt_14th_clip_parsed"

    # 1. get video path
    target_folder_list = get_target_folder_list(
        raw_video_root_path=raw_video_root_path,
        start_time_stemp=start_time_stemp,
        end_time_stemp=end_time_stemp,
        max_video_duration=max_video_duration,
    )
    # print(target_folder_list)

    # 2. save event clip
    save_video(target_folder_list=target_folder_list, save_path=result_path)
