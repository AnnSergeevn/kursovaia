import requests, os, json
from pprint import pprint
from urllib import parse


with open('token.txt', 'r') as file_tok:
    TOKEN = file_tok.read().strip()  # первая строка токен (проверен на проверочном коде)

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def folder_creation(self):
        url = f'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {ya_token}'}
        params = {'path': f'{folder_name}',
                      'overwrite': 'false'}
        response = requests.put(url=url, headers=headers, params=params)

    def upload(self, file_path: str):
        url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {ya_token}'}
        params = {'path': f'{folder_name}/{file_name}',
                      'overwrite': 'true'}

        # Получение ссылки на загрузку
        response = requests.get(url=url, headers=headers, params=params)
        href = response.json().get('href')

            # Загрузка файла
        uploader = requests.put(href, data=open(files_path, 'rb'))


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
        all_photo_count = info['response']['count']  # Количество всех фотографий профиля
        k = len(info['response']['items'])
        new_url = []
        photos = []  # Список всех загруженных фото
        max_size_photo = {}  # Словарь с парой название фото - URL фото максимального разрешения

        # Создаём папку на компьютере для скачивания фотографий
        if not os.path.exists('images_vk'):
            os.mkdir('images_vk')


        for j in range(k):
            n = len(info['response']['items'][j]['sizes']) - 1
            photos_info = {}
            max_size = 0
            for i in range(n):
                url_for_upload = info['response']['items'][j]['sizes'][i]['url']
                all_instances = parse.urlparse(url_for_upload) #распарсеровка пути
                path = all_instances.path
                query = all_instances.query
                # Выбираем фото максимального разрешения и добавляем в словарь max_size_photo
                if path == path and info['response']['items'][j]['sizes'][i]['height'] > info['response']['items'][j]['sizes'][i + 1]['height'] and info['response']['items'][j]['sizes'][i]['width'] > info['response']['items'][j]['sizes'][i + 1]['width']:
                    max_size = info['response']['items'][j]['sizes'][i]['height']


            if info['response']['items'][j]['likes']['count'] not in max_size_photo.keys():
                max_size_photo[info['response']['items'][j]['likes']['count']] = info['response']['items'][j]['sizes'][i]['url']
                photos_info['file_name'] = f"{info['response']['items'][j]['likes']['count']}.jpg"
            else:
                max_size_photo[f"{info['response']['items'][j]['likes']['count']} + {info['response']['items'][j]['date']}"] = info['response']['items'][j]['sizes'][i]['url']
                photos_info['file_name'] = f"{info['response']['items'][j]['likes']['count']}+{info['response']['items'][j]['date']}.jpg"

                photos_info['size'] = info['response']['items'][j]['sizes'][i]['type']
                photos.append(photos_info)

        # Скачиваем фотографии
        for photo_name, photo_url in max_size_photo.items():
            with open('images_vk/%s' % f'{photo_name}.jpg', 'wb') as file:
                img = requests.get(photo_url)
                file.write(img.content)

        print(f'Загружено {len(max_size_photo)} фото')

        # Записываем данные о всех скачанных фоторафиях в файл .json
        with open("photos.json", "w") as file:
            json.dump(photos, file, indent=4)


if __name__ == '__main__':
    user_ID = (int(input("Введите ID пользователя: ")))
    user = VkUser(TOKEN, user_ID)
    info = user.get_profil_photos()
    #pprint(info)
    user.get_all_photos()

    ya_token = str(input('Введите ваш токен ЯндексДиск: '))
    uploader = YaUploader(ya_token)
    folder_name = str(input('Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: '))
    uploader.folder_creation()

    photos_list = os.listdir('images_vk')
    count = 0
    for photo in photos_list:
        file_name = photo
        files_path = os.getcwd() + '\images_vk\\' + photo
        result = uploader.upload(files_path)
        count += 1
        print(f'Фотографий загружено на Яндекс диск: {count}')
 







        #73680897, 687284178, 523800622
