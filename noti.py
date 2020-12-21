from bs4 import BeautifulSoup
# import json
import requests
import signal
import sys
import time


def kill_handler(sig, frame):
    # save data to json file
    sys.exit(0)


def main():
    url_list = [
        'https://manganelo.com/manga/dnha19771568647794',  # Tensei Shitara Slime Datta Ken
        'https://manganelo.com/manga/pn918005'  # Solo Leveling
    ]
    signal.signal(signal.SIGTERM, kill_handler)

    while True:
        for url in url_list:
            req = requests.get(url)
            data = req.text

            soup = BeautifulSoup(data, 'html.parser')
            chapter_list = soup.find('ul', class_='row-content-chapter')
            latest_chapter = chapter_list.li

            prev_chapter_title = ''
            chapter_title = latest_chapter.a.string
            if chapter_title != prev_chapter_title:
                # send notification
                prev_chapter_title = chapter_title
            print(chapter_title)

        time.sleep(5)  # 12 hours


if __name__ == '__main__':
    main()
