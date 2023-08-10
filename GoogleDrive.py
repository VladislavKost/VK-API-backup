from __future__ import print_function

import os.path
import json

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/drive']


class GDriveToken:

    def get_user_token(self):
        creds = None
        if os.path.exists('google_token.json'):
            creds = Credentials.from_authorized_user_file('google_token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'GoogleAppInfo.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('google_token.json', 'w') as token:
                token.write(creds.to_json())
        with open('google_token.json', 'r') as token:
            access_token = json.load(token).get('token')
        return creds, access_token


class GDrive:
    base_url = 'https://www.googleapis.com/drive/v3/files'

    def _get_common_params(self):
        creds = Credentials.from_authorized_user_file('google_token.json', SCOPES)
        with open('google_token.json', 'r') as token:
            access_token = json.load(token).get('token')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        service = build('drive', 'v3', credentials=creds)
        return creds, access_token, headers, service

    def add_folder(self, folder_name):
        creds, access_token, headers, service = self._get_common_params()
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        response = requests.post(self.base_url, headers=headers, data=json.dumps(metadata))
        folder_id = response.json().get('id')
        return folder_id

    def create_folder(self):
        creds, access_token, headers, service = self._get_common_params()
        folder_name = 'vk_photo_backup'
        try:
            results = service.files().list(
                pageSize=100, fields="nextPageToken, files(id, name, trashed)", q=f"name = '{folder_name}'").execute()
            items = results.get('files', [])
            if items == []:
                folder_id = self.add_folder(folder_name)
                return folder_id
            else:
                for item in items:
                    if item['trashed'] == False:
                        folder_id = item['id']
                        return folder_id
                folder_id = self.add_folder(folder_name)
                return folder_id
        except HttpError as error:
            print(f'An error occurred: {error}')

    def add_album_folder(self, album_name, folder_id, headers):
        metadata = {
            'name': album_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id],
        }
        response = requests.post(self.base_url, headers=headers, data=json.dumps(metadata))
        album_id = response.json().get('id')
        return album_id

    def create_album_folder(self, album_name):
        creds, access_token, headers, service = self._get_common_params()
        folder_id = self.create_folder()
        results = service.files().list(
            pageSize=100, fields="nextPageToken, files(id, name, parents, trashed)",
            q=f"name = '{album_name}'").execute()
        items = results.get('files', [])
        if items == []:
            album_id = self.add_album_folder(album_name, folder_id, headers)
            return album_id
        else:
            for item in items:
                if (item != '') and (item['parents'] == [folder_id]) and (item['trashed'] == False):
                    album_id = item['id']
                    return album_id
            album_id = self.add_album_folder(album_name, folder_id, headers)
            return album_id

    def add_photo(self, photo_name, photo_url, access_token, album_id):
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        file = requests.get(photo_url).content
        headers = {
            'Authorization': f'Bearer {access_token}'}
        para = {
            'name': photo_name,
            'parents': [album_id]
        }
        files = {'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
                 'file': file,
                 }
        response = requests.post(url, headers=headers, files=files)

    def upload_photos(self, photo_name, photo_url, album_name):
        album_id = self.create_album_folder(album_name)
        creds, access_token, headers, service = self._get_common_params()

        results = service.files().list(
            pageSize=100, fields="nextPageToken, files(id, name, parents)", q=f"name = '{photo_name}'").execute()
        items = results.get('files', [])
        status = "success"
        if items == []:
            self.add_photo(photo_name, photo_url, access_token, album_id)
            return status
        else:
            for item in items:
                if (item['name'] == photo_name) and (item['parents'] == [album_id]):
                    print(f'Файл с именем {photo_name} в папке {album_name} уже существует!')
                    status = "fail"
                    return status
            self.add_photo(photo_name, photo_url, access_token, album_id)
            return status
