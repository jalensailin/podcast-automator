from glob import glob
import json
import os
import subprocess

# Get paths from secrets file.
with open("./secrets.json") as file:
    secrets = json.load(file)
    input_path = secrets["input_path"]
    output_path = secrets["output_path"]
    remote = secrets["remote"]

# Get most recent file in input directory.
list_of_files = glob(f"{input_path}/*.mkv")
current_file = max(list_of_files, key=os.path.getctime)

# Call ffmpeg on input file.
print(f"Converting file '{os.path.basename(current_file)}' to .mp3")
sp = subprocess.run(
    [
        "ffmpeg",
        "-i",
        current_file,
        "-vn",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "64k",
        f"{output_path}/test.mp3",
    ],
    capture_output=True,
)

podcast = "anaghast"

# Copy file to remote server
ssh_key = os.path.expanduser("~/.ssh/rsync_podcast")
sp = subprocess.run(
    [
        "rsync",
        "-av",
        "--progress",
        "-e",
        f"ssh -i {ssh_key}",
        f"{output_path}/test.mp3",
        f"{remote}:./{podcast}",
    ],
    capture_output=True,
    text=True,  # More human-readable
)

print("STDOUT:", sp.stdout)
print("STDERR:", sp.stderr)
print("Return code:", sp.returncode)
