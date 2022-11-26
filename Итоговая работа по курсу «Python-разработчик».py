import requests
import json
from progress.bar import Bar
from VKToken import VKtoken
from YDToken import YDtoken


class UserVK:

    def __init__(self, URL: str, token: str):
        self.URL = URL
        self.token = token

    def get_photo(self, vk_id: str):
        params = {
            'owner_id': vk_id,
            'album_id': 'profile',
            'rev': '1',
            'extended': '1',
            'access_token': self.token,
            'v': '5.131',
        }
        response = requests.get(self.URL, params=params)
        for response_json in response.json().values():
            with open("Photos_info.json", 'w+') as file_object:
                file_object.write(json.dumps(response_json))
        return response.json()

    @staticmethod
    def parsed_photo(photo_info: dict):
        likes_list = []
        photos_list = []

        for response in photo_info.values():
            for response_key, response_value in response.items():
                if response_key == 'items':
                    for items_list in response_value:
                        photo_dict = {}
                        for photo_info_key, photo_info_value in items_list.items():
                            if photo_info_key == 'date':
                                photo_date = str(photo_info_value)
                            if photo_info_key == 'sizes':
                                for size_params_key, size_params_value in photo_info_value[-1].items():
                                    if size_params_key == 'url':
                                        photo_url = size_params_value
                                        photo_dict.update({'URL': photo_url})
                                    if size_params_key == 'type':
                                        size_type = size_params_value
                                        photo_dict.update({'size': size_type})
                            if photo_info_key == 'likes':
                                for likes_key, likes_value in photo_info_value.items():
                                    if likes_key == 'count':
                                        likes_count = likes_value
                                        if likes_count not in likes_list:
                                            photo_dict.update({'name': likes_count})
                                            photos_list.append(photo_dict)
                                        else:
                                            photo_dict.update({'name': f'{likes_count}-{photo_date}'})
                                            photos_list.append(photo_dict)
        return photos_list


class UserYandex:

    def __init__(self, URL: str, token: str):
        self.URL = URL
        self.token = token


    def create_folder(self, folder_name: str):
        response = requests.put(self.URL,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'OAuth {self.token}'},
                                 params={'path': folder_name})

    @staticmethod
    def upload_file(files, name_dir: str):
        bar = Bar('Processing', max=len(files))
        for file in files:
            for key, value in file.items():
                if key == 'name':
                    name = value
                if key == 'URL':
                    photo_URL = value
            response = requests.post('https://cloud-api.yandex.net:443/v1/disk/resources/upload',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'OAuth {YDtoken}'},
                                 params={'path': f'{name_dir}/{name}', 'url': photo_URL})
            bar.next()
        bar.finish()

def main():
    id_vk = input("Введите id пользователя Vk: ")
    user_vk = UserVK('https://api.vk.com/method/photos.get', VKtoken)
    json_photo = user_vk.get_photo(id_vk)
    parsed_photo = user_vk.parsed_photo(json_photo)
    name_directory = input("Введите название папки: ")
    user_yandex = UserYandex('https://cloud-api.yandex.net:443/v1/disk/resources', YDtoken)
    user_yandex.create_folder(name_directory)
    user_yandex.upload_file(parsed_photo, name_directory)

if __name__ == '__main__':
    main()