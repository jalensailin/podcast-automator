import requests
import json

with open("./secrets.json") as file:
    secrets = json.load(file)
    password = secrets["od_passwd"]
    username = secrets["od_username"]


def od_request(api_path, payload):
    api_base_url = "https://dev.opendrive.com/api/v1"
    if (api_path[0] == "/") or (api_path[0] == "\\"):
        api_path = api_path[1:]
    request_url = f"{api_base_url}/{api_path}"

    response = requests.post(request_url, data=payload)
    response_body = response.json()
    # {'error': {'code': 401, 'message': 'Session does not exist, please re-login.'}}
    if "error" in response_body:
        error_dict = response_body["error"]
        error_message = f"Error {error_dict['code']}. {error_dict['message']}"
        raise ConnectionError(error_message)
    return response_body


# log in and create session ID
login_response = od_request(
    "/session/login.json", {"username": username, "passwd": password}
)
session_id = login_response["SessionID"]
print(session_id)


folder_id_response = od_request(
    "/folder/idbypath.json", {"session_id": session_id, "path": "Music"}
)
folder_id = folder_id_response["FolderId"]
print(folder_id)


logout_response = od_request("/session/logout.json", {"session_id": session_id})
logout_status = logout_response["result"]
print(logout_status)
