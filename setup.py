from setuptools import setup

setup(
      name='kata_scrape',
      version='0.2.2',
      summary='A simple client for scraping Codewars katas',
      description='A simple client for scraping Codewars katas',
      keywords=['codewars', 'code katas', 'selenium'],
      url='https://github.com/jstoebel/kata_scrape',
      author='Jacob Stoebel',
      author_email='jstoebel@gmail.com',
      maintainer='Jacob Stoebel',
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
