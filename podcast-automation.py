from glob import glob
import json
import os

# Load input directory path
with open("./secrets.json") as file:
    secrets = json.load(file)
    dirpath = secrets["directory_path"]

list_of_files = glob(f"{dirpath}/*.mkv")

currentFile = max(list_of_files, key=os.path.getctime)
print(currentFile)

# ffmpeg -output "/some-dir" -input "/some-dir/*.mkv"
