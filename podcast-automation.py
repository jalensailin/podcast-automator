from glob import glob
import json
import os
import subprocess


# Get paths from secrets file.
def get_secrets():
    with open("./secrets.json") as file:
        return json.load(file)


secrets = get_secrets()


# Get most recent file in input directory.
def get_video_file():
    input_path = secrets["input_path"]
    list_of_files = glob(f"{input_path}/*.mkv")
    return max(list_of_files, key=os.path.getctime)


video_file = get_video_file()
video_base_name = os.path.basename(video_file)


# Get podcast name from video file.
def get_podcast_name():
    podcast_name = video_base_name.split("-")[0]
    if podcast_name != "otari" and podcast_name != "anaghast":
        raise Exception(f"Podcast '{podcast_name}' not found.")

    return video_base_name.split("-")[0]


podcast = get_podcast_name()


# Get session number from video file.
def get_session_number():
    mp3_dir = secrets["output_path"]
    list_of_files = glob(f"{mp3_dir}/{podcast}/*.mp3")
    most_recent_file = max(list_of_files, key=os.path.getctime)

    # E.g. "Session 11.mp3" --> "Session 11" --> "11".
    most_recent_session_number = (
        os.path.basename(most_recent_file).split(".")[0].split(" ")[1]
    )

    # Increment session number.
    return int(most_recent_session_number) + 1


session_number = get_session_number()

print(f"Session number: {session_number}; Podcast: {podcast}; Video: {video_base_name}")


# Call ffmpeg on input file.
def convert_to_mp3():
    mp3_dir = secrets["output_path"]
    print(f"Converting file '{video_base_name}' to 'Session {session_number}.mp3'")
    sp = subprocess.run(
        [
            "ffmpeg",
            "-y",  # Overwrite if file already exists.
            "-i",
            video_file,
            "-vn",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "64k",
            f"{mp3_dir}/{podcast}/Session {session_number}.mp3",
        ],
        capture_output=True,
        text=True,
    )

    print("STDOUT:", sp.stdout)
    print("STDERR:", sp.stderr)
    print("Return code:", sp.returncode)


convert_to_mp3()


def send_to_server():
    mp3_dir = secrets["output_path"]
    mp3_file = f"{mp3_dir}/{podcast}/Session {session_number}.mp3"
    remote = secrets["remote"]

    # Copy file to remote server
    ssh_key = os.path.expanduser("~/.ssh/rsync_podcast")
    sp = subprocess.run(
        [
            "rsync",
            "-av",
            "--progress",
            "-e",
            f"ssh -i {ssh_key}",
            f"{mp3_file}",
            # We do not specify a path (and thus use `./`), because the ssh key restricts us via `rrsync` to the correct directory.
            f"{remote}:./{podcast}",
        ],
        capture_output=True,
        text=True,  # More human-readable
    )

    print("STDOUT:", sp.stdout)
    print("STDERR:", sp.stderr)
    print("Return code:", sp.returncode)


send_to_server()
