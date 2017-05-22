import argparse
import json
import os
import random
from shutil import copyfile, copytree
import subprocess

from jinja2 import Template
import requests

from .client import Client

def new_project(args):
    """
    create a new project directory based on arguments
    args: parsed args
    """

    starting_dir = os.getcwd()

    if args['dir']:
        project_dir = os.path.join(os.getcwd(), args['dir'])
    else:
        project_dir = os.path.join(os.getcwd(), 'katas')

    print('creating project directory.')
    os.makedirs(project_dir)

    print('creating config.json...')
    copyfile(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates/config.example.json'),
        os.path.join(project_dir, 'config.json')
    )

    print('copying test utils...')
    copytree(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_utils'),
        os.path.join(project_dir, 'test_utils')
    )

    print('installing node testing dependencies...')
    os.chdir(project_dir)
    pkgs = 'bluebird chai child_process lodash underscore'

    subprocess.check_call('npm install --save {pkgs}'.format(pkgs=pkgs),
                            shell=True)

    os.chdir(starting_dir)

def fetch(args):
    """
    fetch katas based on args
    """
    c = Client(args)
    c.make_kata()

def main():
    if args['which'] == 'init':
        new_project(args)
    elif args['which'] == 'fetch':
        fetch(args)

parser = argparse.ArgumentParser(description='Grab Codewars kata for offline use')
subparsers = parser.add_subparsers()

init_parser = subparsers.add_parser('init', help='create a new Codewars project directory')
init_parser.set_defaults(which='init')
init_parser.add_argument('--dir', help='the path of the project directory, relative to the current directory')

fetch_parser = subparsers.add_parser('fetch', help='fetch katas')
fetch_parser.set_defaults(which='fetch')
fetch_parser.add_argument('--lang', help='The language to grab from')
fetch_parser.add_argument('--n', type=int, help='Number of katas to grab')
fetch_parser.set_defaults(n=1)

args = vars(parser.parse_args())
