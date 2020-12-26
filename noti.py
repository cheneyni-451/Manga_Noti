import json
import re
import signal
import sys
import time

import emailer
import requests
from bs4 import BeautifulSoup


class MangaNotifier:
    save_file = 'save_data.json'

    def __init__(self):
        self.sender_email = 'notifiermanga@gmail.com'
        self.receiver_email = 'cheneyrocks12@gmail.com'

        self.service = emailer.start_mail_service()

        # self.url_list = [
        #     'https://manganelo.com/manga/dnha19771568647794',  # Tensei Shitara Slime Datta Ken
        #     'https://manganelo.com/manga/pn918005',  # Solo Leveling
        #     'invalid',
        #     'https://manganelo.com/manga/vinland_saga',  # Vinland Saga
        #     'https://manganelo.com/manga/ayi2548165456',  # Mairimashita! Iruma-kun
        # ]
        self.url_list = []
        self.prev_chapters = dict()

        with open(MangaNotifier.save_file, 'a+') as fin:
            fin.seek(0)
            data = fin.readline()
            if data:
                self.prev_chapters = json.loads(data)

    def run(self):
        self.get_sources()
        while True:
            i = 0
            while i < len(self.url_list):
                url = self.url_list[i].strip()
                try:
                    data = requests.get(url).text
                except requests.RequestException:
                    self.url_list.pop(i)
                    continue
                soup = BeautifulSoup(data, 'html.parser')

                source = MangaNotifier.get_site(url)

                manga_title = chapter_title = chapter_url = ''
                if source == 'manganelo.com':
                    manga_title, chapter_title, chapter_url = MangaNotifier.parse_manganelo(soup)
                else:
                    print('{} is currently unsupported'.format(source))
                    self.url_list.pop(i)
                    continue

                prev_chapter_title = ''
                if manga_title in self.prev_chapters:
                    prev_chapter_title = self.prev_chapters[manga_title]

                if chapter_title != prev_chapter_title:
                    # send notification
                    self.prev_chapters[manga_title] = chapter_title
                    self.send_noti(manga_title, chapter_title, chapter_url)
                i += 1

            time.sleep(3600)  # 1 hour

    @staticmethod
    def get_site(url: str):
        m = re.search(r'https?://([\w.-]+)/', url)
        return m.group(1)

    @staticmethod
    def parse_manganelo(soup: BeautifulSoup):
        manga_title = soup.h1.string

        chapter_list = soup.find('ul', class_='row-content-chapter')
        latest_chapter = chapter_list.li

        chapter_title = latest_chapter.a.string
        chapter_url = latest_chapter.a.get('href')

        return manga_title, chapter_title, chapter_url

    def get_sources(self):
        try:
            with open('source_list.txt', 'r') as fin:
                self.url_list = list(fin)
        except IOError:
            self.url_list = []
            url = input("URL to Manga or 'quit' to stop: ")
            while url.lower().strip() != 'quit':
                self.url_list.append(url)
                url = input("URL to Manga or 'quit' to stop: ")

    def kill_handler(self, sig, frame):
        # save data to json file
        try:
            with open(MangaNotifier.save_file, 'w') as fout:
                json.dump(self.prev_chapters, fout)
            print("Data Saved Successfully")
        finally:
            sys.exit(0)

    def send_noti(self, manga_title, chap_title, chap_url):
        msg = emailer.create_message('me', self.receiver_email,
                                     "New {title} Chapter".format(title=manga_title),
                                     "{}: {} just came out!\n{}".format(manga_title, chap_title, chap_url))
        emailer.send_message(self.service, 'me', msg)


def main():
    manga_noti = MangaNotifier()
    signal.signal(signal.SIGTERM, manga_noti.kill_handler)

    manga_noti.run()


if __name__ == '__main__':
    main()
