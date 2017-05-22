import copy
import json
import os
import random
import re
import sys
import time

from bs4 import BeautifulSoup
import html2text
from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

from settings import TEMPLATES

class KataExistsError(Exception):
    pass

class Client:

    def __init__(self, args):
        """
        a codewars client.
        args: fetch arguents
        """

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

        self.args = args
        try:
            with(open('config.json', 'r')) as json_reader:
                self.config = json.load(json_reader)
        except FileNotFoundError:
            raise FileNotFoundError("config file not found. Please run `kata-scrape init` first.")

    def make_kata(self):
        """
        create a kata based on args

        post:
            - description is scraped
            - code is scraped
            - tests are scraped
        """

        self._pick_lang()
        print('Finding a kata for {}...'.format(self.language), end='')

        self._get_slug()
        self.url = 'http://www.codewars.com/kata/{slug}/train/{lang}'.format(
            slug=self.slug, lang=self.language
        )
        try:
            os.mkdir(self.slug)
        except FileExistsError:
            raise KataExistsError("You've already scraped the next {} kata.".format(self.language))
        print(' -> {}'.format(self.slug))
        self.kata_dir = os.path.join(os.getcwd(), self.slug)

        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 10).until_not(
                EC.text_to_be_present_in_element((By.ID, 'description'), 'Loading description...')
            )

            # OTHER WAITS GO HERE...
            # I don't know how to wait until the code and tests have been fetched.
            # instead I will just initiate a while loop that breaks when a value is found
            # both of these boxes MUST have a value

            self._scrape_description()
            self._scrape_code()
            self._write_files()

        finally:
            self.driver.quit()

    def _pick_lang(self):
        """
        pick the language to scrape from
        """

        self.language = self.args['lang']
        if self.language is None:
            try:
                self.language = random.choice(self.config['languages'])
            except (KeyError, IndexError) as e:
                raise e("No language given and none specified in config.json")

        language_mapping = {"python": "py", "ruby": "rb", "javascript": "js"}
        self.language_ext = language_mapping[self.language]

    # ~~~ determine the next kata ~~~
    def _get_slug(self):
        """
        language(str): langauge to pull from
        determines a random kata slug
        """

        resp_json = self._train_next()
        self.name = resp_json['name']
        self.slug = resp_json['slug']

    def _train_next(self):
        """
        post request to train in the next challenge
        """

        url = "https://www.codewars.com/api/v1/code-challenges/{}/train".format(self.language)
        data = {'strategy': 'random'}
        headers = {'Authorization': self.config['api_key']}
        resp = requests.post(url, data=data, headers=headers)
        return json.loads(resp.text)

    # ~~~ scrape content and write to file ~~~

    def _scrape_description(self):
        """
        scrape the kata description
        description is saved to object
        """
        print('scraping description', end='')
        t0 = time.time()

        while True:
            try:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                descrip = soup.select('#description')[0]
                break
            except IndexError:
                if time.time() - t0 < 10:
                    time.sleep(.5)
                    continue
                else:
                    # We waited for 10 seconds and we can't find the description
                    # in the DOM. timeout!
                    raise RuntimeError('Kata could not be scraped. Please try again later')

        self.description = ''.join(
            [
                html2text.html2text(
                    str(paragraph)
                ) for paragraph in descrip.findAll('p')
            ]
        )
        print(' -> done')

    def _grab_codemirror(self, _id):
        """
        grab content from the codemirror div
        _id: the id of the div to grab from
        """
        code_box = self.driver.find_elements_by_css_selector('#{} .CodeMirror'.format(_id))[0]
        return self.driver.execute_script('return arguments[0].CodeMirror.getValue()', code_box)

    def _scrape_code(self):
        """
        scrape the starter code and tests
        values are saved to object
        """

        for _id in ['code', 'fixture']:
            while True:
                print('waiting for {}'.format(_id), end='')
                code = self._grab_codemirror(_id)
                if code: # move to next element if something was found, otherwise try again.
                    print(' -> found')
                    setattr(self, _id, code)
                    break

    def _write_files(self):
        """
        write files to disk based on scraped data
        """

        self._write_description()
        self._write_code()

    def _write_description(self):
        """
        write the description file
        """
        with(open('{slug}/description.md'.format(slug=self.slug), 'w+')) as writer:

            descrip_template = open(os.path.join(TEMPLATES, 'description.md.j2'), 'r')
            template = Template(
                descrip_template.read()
            )
            descrip_template.close()
            params = {
                'name': self.name,
                'url': self.url,
                'description': self.description
            }
            output = template.render(**params)
            writer.write(output)

    def _write_code(self):
        """
        write code and tests
        """

        file_mappings = {'code': 'main', 'fixture': 'tests'}
        for k, v in file_mappings.items():

            with open('{slug}/{v}.{ext}'.format(slug=self.slug, v=v, ext=self.language_ext), 'w+') as writer:

                template_h = open(os.path.join(TEMPLATES, k, '{lang}.j2'.format(lang=self.language)),'r')


                template = Template(
                    template_h.read()
                )

                template_h.close()
                # special exception for javascript When the function is
                # scraped we then need to identify its name so we can
                # reference it in the tests

                if k == 'fixture' and self.language == 'javascript':
                    p = re.compile('function\s+(.*?)\(')
                    m = p.search(self.code)

                    try:
                        func_name = m.group(1)
                    except AttributeError:
                        # maybe the format is like this: var someFunc = function(args)
                        p2 = re.compile('(\w+)\s*=\s*function')
                        m2 = p2.search(self.code)
                        func_name = m2.group(1)

                    output = template.render({
                        'code': getattr(self, k),
                        'func_name': func_name
                    })
                else:
                    output = template.render({'code': getattr(self, k)})
                writer.write(output)
