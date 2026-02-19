from glob import glob
import json
import os
import subprocess
import time

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

# See https://stackoverflow.com/questions/42231932/writing-id3-tags-using-easyid3
EasyID3.RegisterTextKey("comment", "COMM")


# Get paths from secrets file.
def get_secrets():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(script_dir, "secrets.json")
    with open(secrets_path) as file:
        return json.load(file)


secrets = get_secrets()


PROCESSED_FILE = "processed.log"  # Convention to use capitalized variable names for values unexpected to change (constants).


def load_processed(podcast_name):
    processed_file = f"{secrets['output_path']}/{podcast_name}/{PROCESSED_FILE}"
    if os.path.exists(processed_file):
        with open(processed_file) as f:
            return set(line.strip() for line in f)
    return set()


def save_processed(podcast_name, video_name):
    processed_file = f"{secrets['output_path']}/{podcast_name}/{PROCESSED_FILE}"
    # "a" for append (write file at the end).
    with open(processed_file, "a") as f:
        f.write(video_name + "\n")


# Get most recent file in input directory.
def get_video_file():
    input_path = secrets["input_path"]

    list_of_files = glob(f"{input_path}/*.mkv")
    video_file = max(list_of_files, key=os.path.getctime)
    video_base_name = os.path.basename(video_file)

    podcast_name = video_base_name.split("-")[0]
    processed_videos = load_processed(podcast_name)
    print(processed_videos)

    if video_base_name in processed_videos:
        print(f"Video '{video_base_name}' has already been processed.")
        return None
    else:
        return video_file


video_file = get_video_file()
if not video_file:
    print("Exiting.")
    exit()

video_base_name = os.path.basename(video_file)


# Get podcast name from video file.
def get_podcast_name():
    podcast_name = video_base_name.split("-")[0]
    allowed_podcasts = ["otari", "anaghast", "deltagreen"]
    if podcast_name not in allowed_podcasts:
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
session_title = f"Session {session_number}"

print(f"Session number: {session_number}; Podcast: {podcast}; Video: {video_base_name}")


# Call ffmpeg on input file.
def convert_to_mp3():
    mp3_dir = secrets["output_path"]
    mp3_file = f"{mp3_dir}/{podcast}/{session_title}.mp3"
    print(f"Converting file '{video_base_name}' to '{os.path.basename(mp3_file)}'")
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
            mp3_file,
        ],
        capture_output=True,
        text=True,
    )

    print("STDOUT:", sp.stdout)
    print("STDERR:", sp.stderr)
    print("Return code:", sp.returncode)

    save_processed(podcast, video_base_name)

    return mp3_file


mp3_file = convert_to_mp3()


def tag_file(mp3_path):
    print(f"✅ Tagging: {os.path.basename(mp3_path)}")
    try:
        audio = EasyID3(mp3_path)
    except ID3NoHeaderError:
        audio = EasyID3()
    audio["title"] = f"{session_title}"

    computer_time = os.path.getctime(mp3_path)
    pretty_time = time.strftime("%Y.%m.%d", time.localtime(computer_time))
    audio["comment"] = f"Recorded {pretty_time}"

    audio.save(mp3_path)


tag_file(mp3_file)


def send_to_server():
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
