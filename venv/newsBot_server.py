import os
import telebot
import requests
from bs4 import BeautifulSoup

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)


class ScraperYandex:
    def __init__(self, keywords):

        self.markup = requests.get('https://yandex.ru/news/').text
        self.keywords = keywords
        self.saved_links = []

    def parse(self):

        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup. findAll('a', {"class": "mg-card__link"})

        for link in links:
            for keyword in self.keywords:
                if keyword.lower() in link.text.lower():
                    self.saved_links.append(link)


class ScraperLenta:
    def __init__(self, keywords):
        self.markup = requests.get('https://lenta.ru/').text
        self.keywords = keywords
        self.saved_links = []

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll('a', {"class": "titles"})
        for link in links:
            for keyword in self.keywords:
                if keyword.lower() in link.text.lower():
                    self.saved_links.append(link)

class ScraperRia:
    def __init__(self, keywords):
        self.markup = requests.get('https://ria.ru/').text
        self.keywords = keywords
        self.saved_links = []

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll('a', {"class": "cell-list__item-link color-font-hover-only"})
        for link in links:
            for keyword in self.keywords:
                if keyword.lower() in link.text.lower():
                    self.saved_links.append(link)

def get_news(message):
  request = message.text.split()
  if len(request) < 2 or request[0].lower() not in 'news':
    return False
  else:
    return True

@bot.message_handler(func=get_news)

def send_news(message):

  #getting the request part of the user input
  request = message.text.split()[1]

  #YANDEX~~~~~~~~~~~~~
  ya = ScraperYandex([request])
  ya.parse()

  #sending an error meassage if there is no news:
  if len(ya.saved_links)  == 0:
    bot.reply_to(message, "No yandex news found for these keywords!")

  else:

    #a bit confusing, but for each link start and end are different
    start = 'href='
    end = 'rel='

    for link in ya.saved_links:

      #format link as needed:
      link = str(link)
      length = len(start)
      a = link.find(start)
      b = link.find(end)
      link_cut = link[(a + length + 1):(b - 2)]

      #sending the link to the user:
      bot.reply_to(message, link_cut)

  #RIA~~~~~~~~~~~~~~~~~~
  ria = ScraperRia([request])
  ria.parse()

  #sending an error meassage if there is no news:
  if len(ria.saved_links) == 0:
    bot.reply_to(message, "No ria news found for these keywords!")

  else:

    #a bit confusing, but for each link start and end are different
    start = 'href='
    end = 'title='

    for link in ria.saved_links:

      #format link as needed:
      link = str(link)
      length = len(start)
      a = link.find(start)
      b = link.find(end)
      link_cut = link[(a + length + 1):(b - 2)]

      #sending the link to the user:
      bot.reply_to(message, link_cut)

  #LENTA~~~~~~~~~~~~~~~
  lenta = ScraperLenta([request])
  lenta.parse()

  #sending an error meassage if there is no news:
  if len(lenta.saved_links)  == 0:
    bot.reply_to(message, "No Lenta news found for these keywords!")

  else:

    #a bit confusing, but for each link start and end are different
    start = 'href='
    end = '<h3'

    for link in lenta.saved_links:

      #format link as needed:
      link = str(link)
      length = len(start)
      a = link.find(start)
      b = link.find(end)
      link_cut = link[(a + length + 1):(b - 2)]
      link_cut = 'https://lenta.ru' + link_cut

      #sending the link to the user:
      bot.reply_to(message, link_cut)

#bot polling function keeps it running
bot.polling()
