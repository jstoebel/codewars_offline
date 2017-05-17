import copy
import json
import os
import random
import re
import subprocess

from bs4 import BeautifulSoup
import html2text
from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.template_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

    def make_kata(self):
        """
        create a kata based on args
        """

        # set language to pull

        try:
            self.language = self.args['lang']
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
            # if self.language == 'javascript':
            #     self._node_dependencies()

        finally:
            self.driver.quit()

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
        self.slug = resp_json['slug']

    def _scrape_description(self):
        """
        scrape the kata description
        description is saved to object
        """
        print('scraping description', end='')
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        descrip = soup.select('#description')[0]

        self.description = ''.join(
            [
                html2text.html2text(
                    str(paragraph)
                ) for paragraph in descrip.findAll('p')
            ]
        )
        print(' -> done')

    def _scrape_code(self):
        """
        scrape the starter code and tests
        values are saved to object
        """

        for _id in ['code', 'fixture']:
            while True:
                print('waiting for {}'.format(_id), end='')
                code_box = self.driver.find_elements_by_css_selector('#{} .CodeMirror'.format(_id))[0]
                code = self.driver.execute_script('return arguments[0].CodeMirror.getValue()', code_box)
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

            template = Template(
                open(os.path.join(self.template_loc, 'description.md.j2'), 'r').read()
            )
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

                template = Template(
                    open(os.path.join(self.template_loc, k, '{lang}.j2'.format(lang=self.language)),'r').read()
                )

                # special exception for javascript When the function is
                # scraped we then need to identify its name so we can
                # reference it in the tests

                if k == 'fixture' and self.language == 'javascript':
                    p = re.compile('function\s*(.*?)\(')
                    m = p.match(self.code)
                    func_name = m.group(1)
                    output = template.render({
                        'code': getattr(self, k),
                        'func_name': func_name
                    })
                else:
                    output = template.render({'code': getattr(self, k)})
                writer.write(output)

    def _node_dependencies(self):
        """
        grab node dependencies for running tests
        """

        os.chdir(self.slug) # cd into kata dir

        subprocess.check_call('npm init -f', shell=True)

        pkgs = 'bluebird chai child_process lodash underscore'
        subprocess.check_call('npm install --save {pkgs}'.format(pkgs=pkgs),
                                shell=True)
