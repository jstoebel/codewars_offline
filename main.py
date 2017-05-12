import argparse
import json
import os
import random
from shutil import copyfile

from jinja2 import Template
import requests

def new_project(args):
    """
    create a new project directory based on arguments
    args: parsed args
    """

    os.makedirs(args['dir'])
    copyfile('templates/config.example.json', os.path.join(args['dir'], 'config.json'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grab Codewars kata for offline use')
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init', help='create a new Codewars project directory')
    init_parser.set_defaults(which='init')
    init_parser.add_argument('--dir', help='the path of the project directory, relative to the current directory')

    fetch_parser = subparsers.add_parser('fetch', help='fetch katas')
    fetch_parser.set_defaults(which='fetch')
    fetch_parser.add_argument('--language', help='The language to grab from')
    fetch_parser.add_argument('--dest', help='The destination of the resulting markdown file')
    fetch_parser.add_argument('--n', type=int, help='Number of katas to grab')

    args = vars(parser.parse_args())

    if args['which'] == 'init':
        print('create a new project directory')
        new_project(args)
    elif args['which'] == 'fetch':
        print('fetch katas')
