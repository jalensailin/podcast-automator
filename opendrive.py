import requests
import json

with open("./secrets.json") as file:
    secrets = json.load(file)
    password = secrets["od_passwd"]
    username = secrets["od_username"]

api_url = "https://dev.opendrive.com/api/v1"

# log in and create session ID
create_session_url = f"{api_url}/session/login.json"
payload = {"username": username, "passwd": password}
response = requests.post(create_session_url, data=payload)
session_id = response.json()["SessionID"]
print(f"Session ID is {session_id}")

# provide folder name, returns folder ID
get_folder_id_url = f"{api_url}/folder/idbypath.json"
payload = {"session_id": session_id, "path": "Music"}
response = requests.post(get_folder_id_url, data=payload)
folder_id = response.json()["FolderId"]
print(f"Folder ID is {folder_id}")

# logout
logout_url = f"{api_url}/session/logout.json"
payload = {"session_id": session_id}
response = requests.post(logout_url, data=payload)
response_dict = response.json()
if (
    "result" in response_dict
):  # if successfully logged out, response is single-dictionary entry with key "result"
    print(f"Logout {response.json()['result']}")
    print("Successfully logged out.")
elif (
    "error" in response_dict
):  # {'error': {'code': 401, 'message': 'Session does not exist, please re-login.'}}
    error_dict = response.json()["error"]
    print(f"Error {error_dict['code']}. {error_dict['message']}")
