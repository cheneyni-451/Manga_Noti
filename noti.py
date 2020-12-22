from bs4 import BeautifulSoup
from getpass import getpass
import json
import requests
import signal
import smtplib
import ssl
import sys
import time

import emailer


class MangaNotifier:
    save_data_fname = 'save_data.json'

    def __init__(self):
        self.sender_email = 'notifiermanga@gmail.com'
        self.receiver_email = 'cheneyrocks12@gmail.com'

        self.service = emailer.start_mail_service()

        self.url_list = [
            'https://manganelo.com/manga/dnha19771568647794',  # Tensei Shitara Slime Datta Ken
            'https://manganelo.com/manga/pn918005'  # Solo Leveling
        ]
        self.prev_chapters = dict()

        with open(MangaNotifier.save_data_fname, 'a+') as fin:
            fin.seek(0)
            data = fin.readline()
            if data:
                self.prev_chapters = json.loads(data)

    def run(self):
        while True:
            for url in self.url_list:
                req = requests.get(url)
                data = req.text

                soup = BeautifulSoup(data, 'html.parser')
                manga_title = soup.h1.string
                print(manga_title)
                chapter_list = soup.find('ul', class_='row-content-chapter')
                latest_chapter = chapter_list.li

                prev_chapter_title = ''
                if manga_title in self.prev_chapters:
                    prev_chapter_title = self.prev_chapters[manga_title]

                chapter_title = latest_chapter.a.string
                if chapter_title != prev_chapter_title:
                    # send notification
                    self.prev_chapters[manga_title] = chapter_title

                    chapter_url = latest_chapter.a.get('href')
                    self.send_noti(manga_title, chapter_title, chapter_url)
                print(chapter_title)

            time.sleep(10)  # 12 hours

    def kill_handler(self, sig, frame):
        # save data to json file
        with open(MangaNotifier.save_data_fname, 'w') as fout:
            json.dump(self.prev_chapters, fout)
        sys.exit(0)

    def send_noti(self, manga_title, chap_title, chap_url):
        msg = emailer.create_message('me', self.receiver_email,
                                     "New {title} Chapter".format(title=manga_title),
                                     "{}: {} just came out! {}".format(manga_title, chap_title, chap_url))
        emailer.send_message(self.service, 'me', msg)


def main():
    manga_noti = MangaNotifier()
    signal.signal(signal.SIGTERM, manga_noti.kill_handler)

    manga_noti.run()


if __name__ == '__main__':
    main()
