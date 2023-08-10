import os

from tqdm import tqdm
from time import sleep
from VKApi import VKToken, VK
from YandexDisk import YandexToken, YandexDisk
from GoogleDrive import GDrive, GDriveToken
from datetime import date

import json


print('Я приветствую вас в своей программе, которая делает резервную копию фотографий из ВК на Яндекс и Гугл диски')
while True:
    disk_choice = int(input('Если вы хотите загрузить фото на Яндекс диск, введите "1", если на Гугл диск - "2": '))
    if disk_choice == 1 or disk_choice == 2:
        break
    else:
        print("Повторите ввод")

vk_get_token = VKToken()
ya_get_token = YandexToken()
gd_get_token = GDriveToken()

vk_token, vk_user_id = vk_get_token.get_user_token_and_id()
if disk_choice == 1:
    ya_token = ya_get_token.get_user_token()
elif disk_choice == 2:
    creds, gd_token = gd_get_token.get_user_token()
while True:
    album_list = ['wall', 'profile', 'saved']
    album_name = input('Введите альбом, из которого нужно сделать backup(wall, profile, saved): ')
    if album_name in album_list:
        break
    else:
        print('Повторите ввод названия альбома с фотографиями')
numb_of_photos = int(input(
    "Введите количество загружаемых фотографий (от новых к старым): "))
vk_client = VK()
photo_list = vk_client.get_photos(album_name)
result_upload = {}
disk = ''
result_list = []
if len(photo_list) < numb_of_photos:
    numb_of_photos = len(photo_list)
for photo_info in tqdm(photo_list[:-numb_of_photos - 1:-1], desc='Total'):
    if disk_choice == 1:
        ya_disk = YandexDisk()
        status = ya_disk.upload_photos(photo_info[0], photo_info[1], album_name)
        disk = "YandexDisk"
        if status == 'success':
            file_name = photo_info[0]
            file_size = photo_info[2]
            file_info = {'photo name': file_name, 'photo size': file_size}
            result_list.append(file_info)
    elif disk_choice == 2:
        gd = GDrive()
        status = gd.upload_photos(photo_info[0], photo_info[1], album_name)
        disk = "GoogleDrive"
        if status == 'success':
            file_name = photo_info[0]
            file_size = photo_info[2]
            file_info = {'photo name': file_name, 'photo size': file_size}
            result_list.append(file_info)
    sleep(0.1)
result = {'disk': disk, 'album': album_name, 'files': result_list}
current_date = date.today()
if os.path.exists(f'{current_date}_backup.json'):
    with open(f'{current_date}_backup.json', 'r') as baskup:
        data = json.load(baskup)
    new_data = []
    new_data.extend(data)
    flag = True
    for num in range(len(data)):
        if (data[num].get('disk') == disk) and (data[num].get('album') == album_name):
            new_data[num] = result
            flag = False
    if flag:
        new_data.append(result)
    with open(f'{current_date}_backup.json', 'w') as result_file:
        result_file.write(json.dumps(new_data))
else:
    with open(f'{current_date}_backup.json', 'w') as result_file:
        result_file.write(json.dumps([result]))
print("Загрузка успешно завершена")
