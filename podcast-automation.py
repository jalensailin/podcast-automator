from glob import glob
import os

dirpath = "/media/jalensailin/Store - HDD (1 TB)/OBS Recordings"
list_of_files = glob(f"{dirpath}/*.mkv")

currentFile = max(list_of_files, key=os.path.getctime)
print(currentFile)

# ffmpeg -output "/some-dir" -input "/some-dir/*.mkv"
