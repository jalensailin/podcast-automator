import requests
import json

with open("./secrets.json") as file:
    secrets = json.load(file)
    password = secrets["passwd"]
    username = secrets["username"]

api_url = "https://dev.opendrive.com/api/v1"

# log in and create session ID
create_session_url= f"{api_url}/session/login.json"
payload = {"username": username, "passwd": password}
response = requests.post(create_session_url,data=payload)
session_id = response.json()["SessionID"]
print(f"Session ID is {session_id}")
# session_id = "8a57a0219ad7a3de18ae44d574281a9aeae2a4826699e96a8fd3bf0192138669"

# provide folder name, returns folder ID
get_folder_id_url = f"{api_url}/folder/idbypath.json"
payload = {"session_id": session_id, "path":  "Music"}
response = requests.post(get_folder_id_url, data=payload)
folder_id = response.json()["FolderId"]
print(f"Folder ID is {folder_id}")
