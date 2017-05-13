import copy
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

        language_mapping = {"python": "py", "ruby": "rb", "javascript": "js"}
        self.language_ext = language_mapping[self.language]

        print('Finding a kata for {}...'.format(self.language))

        self._get_slug()
        self.url = 'http://www.codewars.com/kata/{slug}/train/{lang}'.format(
                                                                    slug=self.slug,
                                                                    lang=self.language
                                                                )
        os.mkdir(self.slug)
        self.kata_dir = os.path.join(os.getcwd(), self.slug)

        self.driver.get(self.url)

        self._scrape_description()
        self._scrape_code()
        self._write_files()

    def _get_slug(self):
        """
        language(str): langauge to pull from
        determines a random kata slug
        """

        url = "https://www.codewars.com/api/v1/code-challenges/{}/train?strategy=random".format(self.language)
        headers = {'Authorization': self.config['api_key']}
        resp = requests.post(url, headers=headers)
        resp_json = json.loads(resp.text)

        self.name = resp_json['name']
        self.username = resp_json['author']
        self.slug = resp_json['slug']

    def _scrape_description(self):
        """
        scrape the kata description
        description is saved to object
        """

        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            try:
                descrip = soup.select('#description')[0]
                break
            except IndexError:
                # data wasn't ready. Just try again.
                continue

        self.description = ''.join(
            [
                html2text.html2text(
                    str(paragraph)
                ) for paragraph in descrip.findAll('p')
            ]
        )

    def _scrape_code(self):
        """
        scrape the starter code and tests
        values are saved to object
        """

        for _id in ['code', 'fixture']:

            code_box = self.driver.find_elements_by_css_selector('#{} .CodeMirror'.format(_id))[0]
            code = self.driver.execute_script('return arguments[0].CodeMirror.getValue()', code_box)
            setattr(self, _id, code)

    def _write_files(self):
        """
        write files to disk based on scrapped data
        """

        # write the description file
        with(open('{slug}/description.md'.format(slug=self.slug), 'w+')) as descrip_writer:
            # print(os.path.dirname(os.path.realpath(__file__)))

            template_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

            desrip_template = Template(
                open(os.path.join(template_loc, 'description.md.j2'), 'w+').read()
            )
            descrip_params = {
                'name': self.name,
                'username': self.username,
                'url': self.url,
                'description': self.description
            }
            descrip_output = desrip_template.render(**descrip_params)
            print(descrip_output)
            descrip_writer.write(descrip_output)

        # write code and tests
        file_mappings = {'code': 'main', 'fixture': 'tests'}
        for k, v in file_mappings.items():

            with open('{slug}/{v}.{ext}'.format(slug=self.slug, v=v, ext=self.language_ext), 'w+') as code_writer:

                code_template = Template(
                    open(os.path.join(template_loc, '{lang}.j2'.format(lang=self.language)),'r').read()
                )

                code_params = {
                    'msg': 'This has been commented out to protect from malicious code.',
                    'code': getattr(self, k)
                }
                code_output = code_template.render(**code_params)
                print(code_output)
                code_writer.write(code_output)
