import requests, os, json
from pprint import pprint
from urllib import parse

with open('token.txt', 'r') as file_tok:
    TOKEN = file_tok.read().strip()  # первая строка токен (проверен на проверочном коде)

class YaUploader:
    def __init__(self, ya_token: str):
        self.token = ya_token


    def folder_creation(self):
        url = f'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {self.token}'}
        params = {'path': f'{folder_name}',
                      'overwrite': 'false'}
        requests.put(url=url, headers=headers, params=params)


    def upload(self, folder_name, data):
        count = 0
        photos = {}
        photos_json=[]
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        for photo in data:
            photo_name = photo.get("file_name")
            file_name = photo_name
            files_path = photo.get("url")
            file_size = photo.get("size")

             # Загрузка файла
            requests.post('https://cloud-api.yandex.net:443/v1/disk/resources/upload',
                     headers=headers,
                     params={
                         'path': f"{folder_name}/{file_name}",
                         'url': f"{files_path}"})
            count += 1
            print(f'Фотографий загружено на Яндекс диск: {count}')

            photos["file_name"] = file_name
            photos["size"] = file_size
            photos_json.append(photos)

        # Записываем данные о всех скачанных фоторафиях в файл .json
        with open("photos.json", "w") as file:
                json.dump(photos_json, file, indent=4)

class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, owner_id):
        self.token = token
        self.owner_id = owner_id


    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131',
            'album_id': 'profile',
            'count': '5',
            'extended': '1',
            'photo_sizes': '1'
        }


    def _build_url(self, api_method):
        return f'{self.url}/{api_method}'


    def get_profil_photos(self):
        params = self.get_common_params()
        params.update({"owner_id": self.owner_id, "album_id": "profile"})
        resource = requests.get(self._build_url("photos.get"), params=params)
        return resource.json()


    def get_all_photos(self):
        info = self.get_profil_photos()
        new_url = []
        photos = []  # Список всех загруженных фото
        max_size_photo = {}  # Словарь с парой название фото - URL фото максимального разрешения

        for photo in info['response']['items']:
            max_size = 0
            photos_info = {}

            # Выбираем фото максимального разрешения и добавляем в словарь max_size_photo
            for size in photo['sizes']:
                if size['height'] >= max_size:
                    max_size = size['height']

            if photo['likes']['count'] not in max_size_photo:
                max_size_photo[photo['likes']['count']] = size['url']
                photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
            else:
                max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = size['url']
                photos_info['file_name'] = f"{photo['likes']['count']}+{photo['date']}.jpg"



            # Формируем список всех фотографий для дальнейшей упаковки в .json

            photos_info['url'] = size['url']
            photos_info['size'] = size['type']
            photos.append(photos_info)

        print(f'Загружено {len(max_size_photo)} фото')
        return photos


if __name__ == '__main__':
    user_ID = (int(input("Введите ID пользователя: ")))
    user = VkUser(TOKEN, user_ID)
    info = user.get_profil_photos()

    ya_token = str(input('Введите ваш токен ЯндексДиск: '))
    uploader = YaUploader(ya_token)
    folder_name = str(input('Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: '))
    uploader.folder_creation()

    photos_list = user.get_all_photos()

    for photo in photos_list:
        photo_name = photo.get("file_name")
        file_name = photo_name
        files_path = photo.get("url")
        file_size = photo.get("size")
    result = uploader.upload(folder_name, photos_list)

    #73680897, 687284178, 523800622
