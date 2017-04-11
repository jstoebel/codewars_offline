import aiohttp
import asyncio
import argparse
import async_timeout
import json
import os
import random

from jinja2 import Template
import requests

class Client:

    def __init__(self, args):
        """
        a codewars client.
        args: command line arguments
        """

        self.args = args
        self.secrets = json.load(open('secrets.json', 'r'))

        # set destination to write kata
        if self.args.dest is not None:
            self.dest = self.args.dest
        else:
            try:
                self.dest = self.secrets['default_home']
            except KeyError:
                raise BaseException("No destination directory given and none specified in secrets.json")

        # validate the destination
        if not os.path.isdir(self.dest):
            raise BaseException("destination path {} does not exsits".format(self.dest))


    def make_kata(self):
        # set language to pull
        default_language = self.args.language

        if self.args.language is not None:
            self.language = self.args.language

        else:
            try:
                self.language = random.choice(self.secrets['languages'])
            except KeyError:
                raise BaseException("No language given and none specified in secrets.json")

        print('Finding a kata for {}'.format(self.language), end='')
        self.get_slug()
        self.get_kata()

    def get_slug(self):
        """
        language(str): langauge to pull from
        determines a random kata slug
        """

        url = "https://www.codewars.com/api/v1/code-challenges/{}/train?strategy=random".format(self.language)
        headers = {'Authorization': self.secrets['api_key']}
        resp = requests.post(url, headers=headers)
        resp_json = json.loads(resp.text)
        self.slug = resp_json['slug']

    def get_kata(self):
        """
        fetches the kata for the given slug

        slug(str): the name of the kata to fetch
        """

        resp = requests.get('https://www.codewars.com/api/v1/code-challenges/{}'.format(self.slug))
        resp_json = json.loads(resp.text)

        params = {
            'slug': self.slug,
            'name': resp_json['name'],
            'username': resp_json['createdBy']['username'],
            'url': resp_json['createdBy']['url'],
            'description': resp_json['description']
        }

        rel_file = os.path.join(self.dest, '{}.md'.format(self.slug))

        with(open(rel_file, 'w+')) as writer:
            template = Template(open('template.md.j2', 'r').read())
            output = template.render(**params)
            writer.write(output)

        print('-> {}'.format(rel_file))

async def main(loop):
    c = Client(ARGS)
    if ARGS.n is None:
        n = 1
    else:
        n = ARGS.n

    async with aiohttp.ClientSession(loop=loop) as session:
        for _ in range(n):
            c.make_kata()


def main():
    c = Client(ARGS)
    for _ in range(ARGS.n):
        c.make_kata()

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Grab Codewars kata for offline use')
    PARSER.add_argument('--language', help='The language to grab from')
    PARSER.add_argument('--dest', help='The destination of the resulting markdown file')
    PARSER.add_argument('--n', type=int, help='Number of katas to grab')
    ARGS = PARSER.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    # main()
