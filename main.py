import requests
from bs4 import BeautifulSoup
import redis
from fuzzywuzzy import process
import telebot
from config import API_KEY

class ScraperYandex:
    def __init__(self, keywords):
        self.markup = requests.get('https://yandex.ru/news/').text
        self.keywords = keywords
        self.saved_links = []

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        print(soup)
        links = soup.findAll('a', {"class": "mg-card__link"})

        for keyword in self.keywords:
            threeLinks = process.extract(keyword, links, limit=3)
            for link in threeLinks:
                print(link)
                val = link[1]
                if val >= 60:
                    self.saved_links.append(link)

    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        for link in self.saved_links:
            r.set(link.text, str(link))


class ScraperRia:
    def __init__(self, keywords):
        self.markup = requests.get('https://ria.ru/').text
        self.keywords = keywords
        self.saved_links = []

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll('a', {"class": "cell-list__item-link color-font-hover-only"})
        print(links)
        for keyword in self.keywords:
            threeLinks = process.extract(keyword, links, limit=3)
            for link in threeLinks:
                print(link)
                val = link[1]
                if val >= 50:
                    self.saved_links.append(link)

    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        for link in self.saved_links:
            r.set(link.text, str(link))

    def email(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        links = [r.get(k) for k in r.keys()]
        r.flushdb()


class ScraperLen:
    def __init__(self, keywords):
        self.markup = requests.get('https://lenta.ru/').text
        self.keywords = keywords
        self.saved_links = []

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')

        links = soup.findAll('a', {"class": "titles"})

        for keyword in self.keywords:
            threeLinks = process.extract(keyword, links, limit=3)
            for link in threeLinks:

                val = link[1]
                if val >= 50:
                    self.saved_links.append(link)

    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        for link in self.saved_links:
            r.set(link.text, str(link))

    def email(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        links = [r.get(k) for k in r.keys()]
        r.flushdb()


def get_news(keyword):
    links = []

    ya = ScraperYandex([keyword]).parse()
    ria = ScraperRia([keyword]).parse()
    lenta = ScraperLen([keyword]).parse()

    # Yandex
    start = 'href='
    end = 'rel='
    for link in ya.saved_links:
        link = str(link)
        length = len(start)
        a = link.find(start)
        b = link.find(end)
        link_cut = link[(a + length + 1):(b - 2)]


    # Ria
    start = 'href='
    end = 'title='
    for link in ria.saved_links:
        link = str(link)
        length = len(start)
        a = link.find(start)
        b = link.find(end)
        link_cut = link[(a + length + 1):(b - 2)]
        links.append(link_cut)

    # Lenta
    start = 'href='
    end = '<h3'
    for link in lenta.saved_links:
        link = str(link)
        length = len(start)
        a = link.find(start)
        b = link.find(end)
        link_cut = link[(a + length + 1):(b - 2)]
        links.append(link_cut)

    return links


# telegram bot part
def telegrambot(api):
    bot = telebot.TeleBot(api)

    @bot.message_handler(content_types="text")
    def send_news(message):
        try:
            links = get_news(str(message))
            bot.send_message(message.chat.id, "Here will be your news in a while...")
            for link in links:
                bot.reply_to(message, link)

        except Exception as ex:
            print(ex)

    bot.polling()

def main():
    telegrambot(API_KEY)


if __name__ == '__main__':
    main()
