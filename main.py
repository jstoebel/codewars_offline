import argparse
import json
import random

from jinja2 import Template
import requests

PARSER = argparse.ArgumentParser(description='Grab Codewars kata for offline use')
PARSER.add_argument('--language', help='The language to grab from')
PARSER.add_argument('--dest', help='The destination of the resulting markdown file')
ARGS = PARSER.parse_args()
SECRETS = json.load(open('secrets.json', 'r'))

def get_kata(slug, api_key, path):
    """
    fetches the kata for the given slug

    slug(str): the name of the kata to fetch
    api_key(str): the user's api key
    dest(optional)(str): the relative path to where the markdown file should be written
    """

    if ARGS.dest is not None:
        dest = ARGS.dest
    else:
        try:
            dest = SECRETS['default_home']
        except KeyError:
            raise BaseException("No destination directory given and none specified in secrets.json")

    resp = requests.get('https://www.codewars.com/api/v1/code-challenges/{}'.format(slug))
    resp_json = json.loads(resp.text)

    params = {
        'slug': slug,
        'name': resp_json['name'],
        'username': resp_json['createdBy']['username'],
        'url': resp_json['createdBy']['url'],
        'description': resp_json['description']
    }
    rel_file = '{rel_path}{file_name}.md'.format(rel_path=dest, file_name=slug)

    with(open(rel_file, 'w+')) as writer:
        template = Template(open('template.md.j2', 'r').read())
        output = template.render(**params)
        writer.write(output)

def get_slug(language, api_key):
    """
    determines a new kata for the user
    returns the slug of the chosen kata
    """
    url = "https://www.codewars.com/api/v1/code-challenges/{}/train?strategy=random".format(language)
    print(url)
    headers = {'Authorization': api_key}
    resp = requests.post(url, headers=headers)
    resp_json = json.loads(resp.text)
    return resp_json['slug']

def get_language(default_language, languages):
    """
    determines the language to pull. Draws first from CLI argument (--language)
    and falls back to secrets.yml. If neither are provided, raises an exception.
    """

    if default_language is not None:
        return default_language

    else:
        try:
            languages = SECRETS['languages']
            return random.choice(languages)
        except KeyError:
            raise BaseException("No language given and none specified in secrets.json")

def main():
    api_key = SECRETS['api_key']
    language = get_language(ARGS.language, SECRETS['languages'])
    slug = get_slug(language, api_key)
    get_kata(slug, api_key, ARGS.dest)

if __name__ == '__main__':
    main()
