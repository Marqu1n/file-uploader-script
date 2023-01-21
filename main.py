from __future__ import print_function
import os, stat
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from apiclient import errors
import os
import zipfile as zp


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


def file_check(creds, FILE):
    creds = creds

    try:
        # TODO - Check if the file is already in Google Drive
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


def zipFoulder(p1, p2):
    def initialDirs(files):
        global dirs
        dirs = []
        for i in files:
            if i.is_dir():
                dirs.append(i)
        return dirs

    try:
        with zp.ZipFile(
            p1,
            "w",
        ) as myzip:

            dirs = initialDirs(os.scandir(p2))

            for i in dirs:
                dirCheck = os.scandir(i)
                for j in dirCheck:
                    if j.is_dir():
                        dirs.append(j)
                    else:
                        myzip.write(j.path)

    except zp.BadZipFile as error:
        print(f"Bad Zip Error: {error}")


def list_items(creds):

    service = build("drive", "v3", credentials=creds)
    results = service.files().list(fields="nextPageToken,files(id,name)").execute()
    items = results.get("files", [])
    return items


def create_folder(creds, name):
    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        file_metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields="id").execute()
        print(f'Folder ID: "{file.get("id")}".')
        return file.get("id")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def file_upload(FILE_PATH, FILE_METADATA, creds, mimetype):
    service = build("drive", "v3", credentials=creds)

    media = MediaFileUpload(
        FILE_PATH,
        mimetype=mimetype,
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
    if os.path.exists("C:\Scripts\\file uploader\\token.json"):
        creds = Credentials.from_authorized_user_file(
            "C:\Scripts\\file uploader\\token.json", SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "C:\Scripts\\file uploader\credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("C:\Scripts\\file uploader\\token.json", "w") as token:
            token.write(creds.to_json())
    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        # create a list of all drive files
        items = list_items(creds)

        # upload cfg
        NAME1 = "cfg.cfg"
        PATH1 = "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg\meu_cfg.cfg"
        os.chmod(
            path="C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg",
            mode=stat.S_IROTH,
        )
        if file_check(creds, FILE=NAME1):
            # Uploads cfg file to Google Drive
            METADATA = {"name": NAME1}
            file_upload(PATH1, METADATA, creds, "text/plain")

        else:
            FILE_ID = [item["id"] for item in items if item["name"] == "cfg.cfg"]
            service.files().delete(fileId=FILE_ID[0]).execute()
            METADATA = {"name": NAME1}
            file_upload(PATH1, METADATA, creds, "text/plain")

        # upload minecraft world
        NAME2 = "Minecraft World.zip"
        PATH2 = "C:\\Users\\Ferba\\AppData\\Roaming\\.minecraft\\saves\\Mundo Mine.zip"
        os.chmod(
            path="C:\\Users\\Ferba\\AppData\\Roaming\\.minecraft\\saves",
            mode=stat.S_IROTH,
        )

        if file_check(creds, FILE="Worlds"):
            create_folder(creds, "Worlds")

        folder_id = [item["id"] for item in items if item["name"] == "Worlds"]

        if file_check(creds, FILE=NAME2):
            # Uploads Minecraft world to Google Drive
            METADATA = {"name": NAME2, "parents": folder_id}
            zipFoulder(
                p1=PATH2, p2="C:\\Users\\Ferba\\AppData\\Roaming\\.minecraft\\saves"
            )
            file_upload(PATH2, METADATA, creds, "application/x-rar-compressed")
        else:
            # create a list of all drive files
            FILE_ID = [
                item["id"] for item in items if item["name"] == "Minecraft World"
            ]
            METADATA = {"name": NAME2, "parents": folder_id}
            service.files().delete(fileId=FILE_ID[0]).execute()
            zipFoulder()
            file_upload(PATH2, METADATA, creds, "application/x-rar-compressed")

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None


if __name__ == "__main__":
    main()
