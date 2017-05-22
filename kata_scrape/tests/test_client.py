import os
from shutil import copyfile, rmtree
import sys
import unittest
from unittest.mock import MagicMock

TEST_ROOT = os.path.dirname((os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(TEST_ROOT, '..'))
import client

class TestClient(unittest.TestCase):

    def setUp(self):
        self.kata_setup()
        os.chdir(os.path.join(TEST_ROOT, 'katas'))

    def kata_setup(self):
        # create a katas folder with a config file

        os.makedirs(os.path.join(TEST_ROOT, 'katas'))
        copyfile(
            os.path.join(TEST_ROOT, 'test_files/config.json'),
            os.path.join(TEST_ROOT, 'katas/config.json')
        )

    def tearDown(self):
        """
        remove the katas directory
        """
        os.chdir(TEST_ROOT)
        rmtree(os.path.join(TEST_ROOT, 'katas'))

    def test__pick_lang(self):
        """
        langauge specified by user
        """

        c = client.Client({'lang': 'python'})
        c._pick_lang()
        self.assertEqual(c.language, 'python')

    def test__pick_lang_random(self):
        """
        user specifies no language
        """

        c = client.Client({'lang': None})
        c._pick_lang()
        self.assertIn(c.language, ["python", "ruby", "javascript"])

    def test__get_slug(self):
        """
        need to mock _train_next
        """

        c = client.Client({})
        resp_json = {'name': 'Jacob', 'slug': 'new-kata'}
        c._train_next = MagicMock(return_value=resp_json)
        c._get_slug()
        # assert that name and slug are set
        self.assertEqual('Jacob', c.name)
        self.assertEqual('new-kata', c.slug)
        c._train_next.assert_called_with()

    def test__scrape_description(self):
        """
        mock self.driver.page_source
        page description should be saved, parsed as markdown
        """
        c = client.Client({})
        descrip_html = """
        <div>
            <div id="description">
                <p> first block </p>
                <p> second block </p>
            </div>
        </div>
        """

        c = client.Client({})
        c.driver = MagicMock()
        c.driver.page_source = descrip_html

        c._scrape_description()
        expected_description = 'first block\n\nsecond block\n\n'
        self.assertEqual(c.description, expected_description)

    def test__scrape_description_timeout(self):
        """
        mock _grab_description
        description not found, timesout
        """

        c = client.Client({})
        descrip_html = """
        <div>
            description is loading...
        </div>
        """

        c = client.Client({})
        c.driver = MagicMock()
        c.driver.page_source = descrip_html
        with self.assertRaises(RuntimeError) as cm:
            c._scrape_description()

        err = cm.exception
        self.assertEqual(str(err), 'Kata could not be scraped. Please try again later')

    def test__scrape_code(self):
        """
        mock _grab_codemirror
        """

        c = client.Client({})
        c._grab_codemirror = MagicMock(return_value="some code")
        c._scrape_code()

        for _id in ['code', 'fixture']:
            self.assertEqual(getattr(c, _id), "some code")

        self.assertEqual(c._grab_codemirror.call_count, 2)

    def test__write_description(self):
        c = client.Client({})
        c.slug = 'some-kata'
        c.name = 'jacob'
        c.url = 'www.someurl.com'
        c.description = 'kata description'

        expected_file = '# {name}\n[{url}]({url})\n\n{description}'.format(
            name=c.name,
            url=c.url,
            description=c.description
        )
        os.makedirs(c.slug)
        c._write_description()

        with(open('./{}/description.md'.format(c.slug), 'r')) as reader:
            self.assertEqual(expected_file, reader.read())

    def test__write_code(self):
        c = client.Client({})
        c.slug = 'some-kata'
        c.code = 'some code'
        c.fixture = 'a fixture'
        c.language = 'python'
        c.language_ext = 'py'

        os.makedirs(c.slug)

        expected_code_file = '"""\nThis has been commented out to protect from malicious code\n\n{code}\n"""'.format(
            code=c.code
        )

        expected_test_file = '''import sys
sys.path.append('../test_utils/python')
import test_utils as test
Test = test # this module is sometimes referenced with a capital T
from main import *

{code}'''.format(code=c.fixture)

        c._write_code()

        with(open('./{}/main.py'.format(c.slug), 'r')) as reader:
            self.assertMultiLineEqual(expected_code_file, reader.read())


        with(open('./{}/tests.py'.format(c.slug), 'r')) as reader:
            self.assertMultiLineEqual(expected_test_file, reader.read())

#     def test__write_code_js(self):
#         c = client.Client({})
#         c.slug = 'some-kata'
#         c.fixture = 'a fixture'
#         c.language = 'javascript'
#         c.language_ext = 'js'
#
#         os.makedirs(c.slug)
#
#         c.code = 'function someFunc(args){\n\n}'
#
#         expected_test_file = """var Test = require('../test_utils/javascript/test_utils'),
#   {func_name} = require('./main')
#
# {code}""".format(code=c.code, func_name='someFunc')
#
#         c._write_code()
#
#         with(open('./{}/tests.py'.format(c.slug), 'r')) as reader:
#             self.assertMultiLineEqual(expected_test_file, reader.read())

    def test__write_code_js(self):
        c = client.Client({})
        c.slug = 'some-kata'
        c.fixture = 'a fixture'
        c.language = 'javascript'
        c.language_ext = 'js'

        os.makedirs(c.slug)

        functions = [
            'var someFunc = function(args){\n}',
            'function someFunc(args){\n}'
        ]

        for func_name in functions:
            c.code = func_name
            expected_test_file = """var Test = require('../test_utils/javascript/test_utils'),
  {func_name} = require('./main')

{code}""".format(code=c.fixture, func_name='someFunc')

            c._write_code()

            with(open('./{}/tests.js'.format(c.slug), 'r')) as reader:
                self.assertMultiLineEqual(expected_test_file, reader.read())

if __name__ == '__main__':
    unittest.main()
