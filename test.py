import random
import time
from config import CHANNEL_ID, API_KEY, FILE_NAME, SHORTENER_TOKEN
import requests
from bs4 import BeautifulSoup
import telebot
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

'''TELEGRAM BOT LOGIN'''
BOT_API_KEY = API_KEY
bot = telebot.TeleBot(BOT_API_KEY)

'''Shortener'''
api_key = SHORTENER_TOKEN



'''HTML Scraping (news)'''


class ScraperYandex:
    def __init__(self):
        self.url = 'https://yandex.ru/news/'
        self.markup = requests.get(self.url).text
        self.saved_links = []
        self.available_themes = []
        self.available_themeslinks = []
        self.soup = BeautifulSoup(self.markup, 'html.parser')

    def most_popular_news(self):
        soup = self.soup
        url = self.url
        captcha = self.soup.findAll('div', {"class": "CheckboxCaptcha"})

        if captcha != []:
            print("captcha encounter!")

        self.markup = requests.get(url).text

        links = soup.findAll('a', {"class": "mg-card__link"})
        for item in links:
            item = str(item)
            link = item.split('href="')[1].split('" rel')[0]
            self.saved_links.append(link)
        return self.saved_links

    def get_categories(self):
        captcha = self.soup.findAll('div', {"class": "CheckboxCaptcha"})

        if captcha != []:
            print("captcha encounter!")

        themes_spans = self.soup.findAll('span', {"class": "news-navigation-menu__title"})
        themes_links = self.soup.findAll('a', {"class": "news-navigation-menu__item"})
        dictionary = {}

        for item in themes_spans:
            item = str(item)
            theme_name = item.split('>')[1].split('<')[0]
            self.available_themes.append(theme_name)

        for item in themes_links:
            item = str(item)
            theme_link = item.split('href="')[1].split('" rel')[0]
            self.available_themeslinks.append(theme_link)

        i = 0
        for item in self.available_themes:
            dictionary.update({item: self.available_themeslinks[i]})
            i += 1

        if len(self.available_themes) != len(themes_links):
            print("error in lengths of arrays. Not able to create categories dictionary!")
            return Exception
        return self.available_themes, dictionary


def get_tags():
    tags_list = []
    try:
        tags_url = 'https://ria.ru/tags/?page=1'
        markup = requests.get(tags_url).text
        soup = BeautifulSoup(markup, 'html.parser')

        tags = soup.findAll('a', {'class': 'tags__list-item'})
        for item in tags:
            item = str(item)
            tags_trim = item.split('>')[1].split('</')[0]
            tags_list.append(tags_trim)
        top10 = tags_list[:10]
        return top10
    except Exception as ex:
        print(ex)


def get_news(keyword):
    result_list = []
    categories = ScraperYandex(keyword).get_categories()[0]
    print("Категории: " + str(categories))

    try:
        random_categorie = random.choice(categories)
        print("Случайный выбор категории: " + str(random_categorie))

        dictionary = ScraperYandex(keyword).get_categories()[1]
        random_categorie_link = dictionary[str(random_categorie)]
        print("Значение ключа из наших ссылок: " + str(random_categorie_link))

        news_list = str(ScraperYandex(keyword).most_popular_news())
        for item in news_list:
            item = str(item)
            item_trim = item.split('href="')[1].split('" rel')[0]
            result_list.append(item_trim)

        print("Список самых популярных новостей на сейчас: " + str(result_list))

    except Exception as ex:
        print(ex)


def write_news_to_file(keyword, file_name, links_list):
    links_list_sorted = process.extract(keyword, links_list, limit=14)

    with open(file_name, 'w') as file:
        for item in links_list_sorted:
            item = str(item[0])
            file.write(item + '\n')


'''Telegram bot'''


def telegrambot(message):

    bot.send_message(chat_id=CHANNEL_ID, text=message)


'''Main function (maintenance)'''


def main():
    links_list = open(FILE_NAME).readlines()
    print("links read are: " + str(links_list))

    lower_bound = 1
    while True:
        links_left = len(links_list)
        print("amount of links there are left: " + str(links_left))

        try:
            top10tags = get_tags()
            random_tag = random.choice(top10tags)
            print('random tag is: ' + random_tag)

            if links_left < lower_bound:
                print('Need to go set some news...')
                links = ScraperYandex().most_popular_news()
                write_news_to_file(random_tag, FILE_NAME, links)
                links_list = open(FILE_NAME).readlines()
            link = links_list[0]
            print(str(link))
            url = str(link)
            api_url = f"https://cutt.ly/api/api.php?key={api_key}&short={url}"
            data = requests.get(api_url).json()["url"]
            if data["status"] == 7:
                shortened_url = data["shortLink"]
                telegrambot(shortened_url)
                print("The link is sent!")
                links_list.pop(0)
                with open(FILE_NAME, 'w') as file:
                    for item in links_list:
                        item = str(item)
                        file.write(item)
            else:
                print("[!] Error Shortening URL:", data)

        except Exception as ex:
            print('Error encountered: ' + str(ex))

        print('Going to sleep for a while...')
        sleep_time = random.randint(2400, 3600)
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()
