import os.path
import shutil

import requests


class Downloader:

    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36',
        'accept': '*/*'
    }

    def __init__(self, url):
        self.url = url

    def download(self):
        m3u8_url = self.get_m3u8_list()
        self.get_link_from_m3u8()
        seg_count = int(self.get_segment_count())
        dwnl_link = self.get_download_link()
        self.get_download_segment(dwnl_link, seg_count)
        return self.merge_ts(m3u8_url[0], m3u8_url[1], seg_count)

    def get_m3u8_list(self):
        url = self.url.split("/")[-2]
        req = requests.get(
            url=f'https://rutube.ru/api/play/options/{url}/?no_404=true&referer=https%3A%2F%2Frutube.ru',
            headers=Downloader.HEADERS)
        video_data = req.json()
        video_author = video_data['author']['name']
        video_title = video_data['title']
        dict_repl = ["/", "\\", "[", "]", "?", "'", '"', ":", "."]
        for repl in dict_repl:
            if repl in video_title:
                video_title = video_title.replace(repl, "")
            if repl in video_author:
                video_author = video_author.replace(repl, "")
        video_title = video_title.replace(" ", "_")
        video_author = video_author.replace(" ", "_")
        video_m3u8 = video_data['video_balancer']['m3u8']
        return video_author, video_title, video_m3u8

    def get_link_from_m3u8(self):
        if not os.path.isdir('Audio'):
            os.mkdir('Audio')
        req = requests.get(
            url=self.get_m3u8_list()[2],
            headers=Downloader.HEADERS)
        data_m3u8_dict = []
        with open('Audio\\pl_list.txt', 'w', encoding='utf-8') as file:
            file.write(req.text)
        with open('Audio\\pl_list.txt', 'r', encoding='utf-8') as file:
            src = file.readlines()

        for item in src:
            data_m3u8_dict.append(item)

        url_playlist = data_m3u8_dict[-1]
        return url_playlist

    def get_segment_count(self):
        req = requests.get(url=self.get_link_from_m3u8(), headers=Downloader.HEADERS)
        data_seg_dict = []
        for seg in req:
            data_seg_dict.append(seg)
        seg_count = str(data_seg_dict[-2]).split("/")[-1].split("-")[1]
        return seg_count

    def get_download_link(self):
        link = f'{self.get_link_from_m3u8().split(".m3u8")[0]}/'
        return link

    def get_download_segment(self, link, count):
        for item in range(1, count+1):
            print(f'[+] - Загружаю сегмент {item}/{count}')
            req = requests.get(f'{link}segment-{item}-v1-a1.ts')
            with open(f'Audio\\segment-{item}-v1-a1.ts', 'wb') as file:
                file.write(req.content)
        print('[INFO] - Все сегменты загружены')

    def merge_ts(self, author, title, count):
        with open(f'Audio\\{title}.ts', 'wb') as merged:
            for ts in range(1, count+1):
                with open(f'Audio\\segment-{ts}-v1-a1.ts', 'rb') as mergefile:
                    shutil.copyfileobj(mergefile, merged)
        os.system(f"ffmpeg -i Audio\\{title}.ts Audio\\{title}.opus")
        print('[+] - Конвертирование завершено')
        return f"Audio\\{title}.opus"
