import json
import os
from datetime import datetime as d
from urllib.parse import urlencode

import webbrowser
import requests


class VKToken:
    """Класс для получения токена и id пользователя VK"""
    with open('VKAppInfo.json', 'r') as id:
        APP_ID = json.load(id).get('APP_ID')
    base_url = 'https://oauth.vk.com/authorize'
    params = {'client_id': APP_ID,
              'display': 'page',
              'redirect_uri': 'https://oauth.vk.com/blank.html',
              'scope': 'photos',
              'response_type': 'token'
              }

    def get_user_token_and_id(self):
        if os.path.exists('vk_token.json'):
            with open('vk_token.json', 'r') as token:
                vk_token = json.load(token)
            user_vk_id = vk_token.get('user_vk_id')
            access_token = vk_token.get('access_token')
        else:
            link = f'{self.base_url}?{urlencode(self.params)}'
            print("Для доступа к ВК перейдите по ссылке, авторизуйтесь, "
                  "скопируйте URL в адресной строке браузера и вставьте ниже")
            print(link)
            webbrowser.open_new_tab(link)
            user_url = input('Вставьте ссылку: ')
            access_token = user_url[user_url.find('access_token=') + len('access_token='):user_url.find('expires_in')-1]
            user_vk_id = user_url[user_url.find('user_id=') + len('user_id='):]
            info = {'user_vk_id': str(user_vk_id), 'access_token': str(access_token)}
            with open('vk_token.json', 'w') as token:
                token.write(json.dumps(info))
        return access_token, user_vk_id


class VK:
    """Класс описывает методы для получения фотографий из ВК"""
    def __init__(self):
        self.API_BASE_URL = 'https://api.vk.com/method/'
        with open('vk_token.json', 'r') as token:
            vk_token = json.load(token)
        self.user_vk_id = vk_token.get('user_vk_id')
        self.access_token = vk_token.get('access_token')

    # Общие параметры класса
    def get_common_params(self):
        return {
            'access_token': self.access_token,
            'v': '5.131'
        }

    # Получение списка с фотографиями пользователя и названиями для сохранения файлов
    def get_photos(self, photo_album):
        params = self.get_common_params()
        params.update({
            'owner_id': self.user_vk_id,
            'album_id': photo_album,
            'extended': '1',
        })
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        photos = response.json().get('response', {}).get('items', [])
        photo_list = []
        for photo in photos:
            photo_info = []
            photo_url = photo.get('sizes', '')[-1].get('url', '')
            photo_size = photo.get('sizes', '')[-1].get('type', '')
            photo_likes = photo['likes']['count']
            photo_date = d.fromtimestamp(int(photo['date'])).strftime('%d-%m-%Y')
            photo_name = f'{photo_likes}_{photo_date}.jpg'
            photo_info.append(photo_name)
            photo_info.append(photo_url)
            photo_info.append(photo_size)
            photo_list.append(photo_info)
        return photo_list
