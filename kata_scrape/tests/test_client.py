import os
from shutil import copyfile, rmtree
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(1, '..')
import client

class TestClient(unittest.TestCase):

    def setUp(self):
        self.test_root = os.getcwd()
        self.kata_setup()
        os.chdir('katas')

    def kata_setup(self):
        # create a katas folder with a config file

        os.makedirs('./katas')
        copyfile(
        'test_files/config.json',
        'katas/config.json'
        )

    def tearDown(self):
        """
        remove the katas directory
        """
        os.chdir(self.test_root)
        rmtree('./katas')

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
        pass

    def test__write_code(self):
        pass

    def test__write_code_js(self):
        pass

if __name__ == '__main__':
    unittest.main()
