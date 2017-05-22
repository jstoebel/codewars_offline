from setuptools import setup

setup(name='kata_scrape',
      version='0.1',
      description='A simple client for scraping Codewars katas',
      url='https://github.com/jstoebel/kata_scrape',
      author='Jacob Stoebel',
      author_email='jstoebel@gmail.com',
      license='MIT',
      packages=['kata_scrape'],
      scripts=['bin/kata-scrape'],
      zip_safe=False,
      include_package_data=True,
      install_requires=[
        'Jinja2',
        'requests',
        'bs4',
        'html2text',
        'selenium'
      ],
      )
