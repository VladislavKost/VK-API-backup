import json
import os
from urllib.parse import urlencode

import webbrowser
import requests


class YandexToken:
    """Класс для получения токена пользователя Яндекса"""
    with open('YandexAppInfo.json', 'r') as id:
        APP_ID = json.load(id).get('APP_ID')
    base_url = 'https://oauth.yandex.ru/authorize'
    params = {'client_id': APP_ID,
              'response_type': 'token'
              }

    def get_user_token(self):
        if os.path.exists('yandex_token.json'):
            with open('yandex_token.json', 'r') as token:
                access_token = json.load(token).get('token')
        else:
            link = f'{self.base_url}?{urlencode(self.params)}'
            print(
                "Для доступа к Яндекс Диску перейдите по ссылке, авторизуйтесь, "
                "скопируйте URL в адресной строке браузера и вставьте ниже")
            print(link)
            webbrowser.open_new_tab(link)
            user_url = input('Вставьте ссылку: ')
            if user_url.find('access_token=') != -1:
                access_token = user_url[
                               user_url.find('access_token=') + len('access_token='):user_url.find('token_type') - 1]

            else:
                access_token = user_url
            info = {'token': access_token}
            with open('yandex_token.json', 'w') as token:
                token.write(json.dumps(info))
        return access_token


class YandexDisk:
    """Класс описывает методы загрузки фотографий на яндекс диск"""
    def __init__(self):
        self.BASE_YA_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.params = {
           'path': 'vk_photo_backup'
        }
        with open('yandex_token.json', 'r') as token:
            self.access_token = json.load(token).get('token')
        self.headers = {
              'Authorization': self.access_token
           }

    def create_folder(self, album_name):
        response = requests.put(f'{self.BASE_YA_URL}', params=self.params, headers=self.headers)
        if 'error' in response.json():
            pass
        self.params['path'] = f'vk_photo_backup/{album_name}'
        response = requests.put(f'{self.BASE_YA_URL}', params=self.params, headers=self.headers)
        if 'error' in response.json():
            pass

    def get_upload_url(self, photo_name, album_name):
        self.create_folder(album_name)
        self.params['path'] = f'vk_photo_backup/{album_name}/{photo_name}'
        url = requests.get(f'{self.BASE_YA_URL}/upload', params=self.params, headers=self.headers)
        return url.json().get('href', '')

    def upload_photos(self, photo_name, photo_url, album_name):
        try:
            url = self.get_upload_url(photo_name, album_name)
            file = requests.get(photo_url).content
            response = requests.put(url, files={'file': file})
            status = "success"
            return status
        except requests.exceptions.MissingSchema:
            print(f'Файл с именем {photo_name} был загружен ранее. '
                  f'Чтобы его обновить, удалите его и повторите попытку снова.')
            status = 'fail'
            return status
