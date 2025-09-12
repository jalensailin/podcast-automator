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


# Call ffmpeg on input file.
def convert_to_mp3():
    input_file = get_video_file()
    output_path = secrets["output_path"]
    print(f"Converting file '{os.path.basename(input_file)}' to .mp3")
    sp = subprocess.run(
        [
            "ffmpeg",
            "-y",  # Overwrite if file already exists.
            "-i",
            input_file,
            "-vn",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "64k",
            f"{output_path}/test.mp3",
        ],
        capture_output=True,
        text=True,
    )

    print("STDOUT:", sp.stdout)
    print("STDERR:", sp.stderr)
    print("Return code:", sp.returncode)


convert_to_mp3()


def send_to_server():
    podcast = "anaghast"
    mp3_file = f"{secrets['output_path']}/test.mp3"
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
            f"{remote}:./{podcast}",
        ],
        capture_output=True,
        text=True,  # More human-readable
    )

    print("STDOUT:", sp.stdout)
    print("STDERR:", sp.stderr)
    print("Return code:", sp.returncode)


send_to_server()
