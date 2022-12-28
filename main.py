from __future__ import print_function
import os, stat
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from apiclient import errors

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


def file_check(FILE):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        # build Google drive service
        service = build("drive", "v3", credentials=creds)

        # return a list of all items in Google Drive
        results = service.files().list(fields="nextPageToken,files(id,name)").execute()
        items = results.get("files", [])
        file_names = []
        file_names += [
            item["name"].encode("utf-8").decode("ascii", "ignore") for item in items
        ]

        if FILE in file_names:
            return False
        else:
            return True

    except HttpError as error:
        print(f"HttpError: {error}")


# uploads file
def file_upload(FILE_PATH, FILE_METADATA, creds):
    service = build("drive", "v3", credentials=creds)
    os.chmod(
        path="C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg",
        mode=stat.S_IROTH,
    )
    media = MediaFileUpload(
        FILE_PATH,
        mimetype="https://mimetype.io/all-types/",
    )
    # pylint: disable=maybe-no-member
    file = (
        service.files()
        .create(body=FILE_METADATA, media_body=media, fields="id")
        .execute()
    )
    print(f'File ID: {file.get("id")}')
    print(f"Full link:https://drive.google.com/file/d/{file.get('id')}/view ")


def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        NAME = "name you want"
        PATH = "file path"
        if file_check(FILE=NAME):
            # Uploads cfg file to Google Drive
            METADATA = {"name": NAME}
            file_upload(PATH, METADATA, creds)

        else:
            # create a list of all drive files
            results = (
                service.files().list(fields="nextPageToken,files(id,name)").execute()
            )
            items = results.get("files", [])
            FILE_ID = [item["id"] for item in items if item["name"] == "cfg.cfg"]
            service.files().delete(fileId=FILE_ID[0]).execute()
            METADATA = {"name": NAME}
            file_upload(PATH, METADATA, creds)

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None


if __name__ == "__main__":
    main()
