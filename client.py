import json
import os
import random

from bs4 import BeautifulSoup
import html2text
from jinja2 import Template
from selenium import webdriver
import requests

class Client:

    def __init__(self, args):
        """
        a codewars client.
        args: fetch arguents
        """

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

        self.args = args
        self.config = json.load(open('config.json', 'r'))

    def make_kata(self):
        """
        create a kata based on args
        """

        # set language to pull

        try:
            self.language = self.args['language']
        except KeyError:
            try:
                self.language = random.choice(self.config['languages'])
            except (KeyError, IndexError) as e:
                raise e("No language given and none specified in config.json")

        print('Finding a kata for {}...'.format(self.language))

        self._get_slug()
        self.url = 'http://www.codewars.com/kata/{slug}/train/{lang}'.format(
                                                                    slug=self.slug,
                                                                    lang=self.language
                                                                )
        # os.mkdir(self.slug) UNCOMMENT ME!
        self._scrape_kata()
        # write files

    def _get_slug(self):
        """
        language(str): langauge to pull from
        determines a random kata slug
        """

        url = "https://www.codewars.com/api/v1/code-challenges/{}/train?strategy=random".format(self.language)
        headers = {'Authorization': self.config['api_key']}
        resp = requests.post(url, headers=headers)
        resp_json = json.loads(resp.text)
        self.slug = resp_json['slug']

    def _scrape_kata(self):
        """
        scrape the kata for description, starter code and tests

        description, starter code and tests are written to disk as files
        """
        # self.url = "http://www.codewars.com/kata/valid-braces/train/ruby"
        # print(self.url)
        self.driver.get(self.url)

        # resp = requests.get(self.url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        descrip = soup.select('#description')[0]

        for paragraph in descrip.findAll('p'):
            print(str(paragraph))
            print(html2text.html2text(str(paragraph)))

        # print(soup.select('#description')[0])
