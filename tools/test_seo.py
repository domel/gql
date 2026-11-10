"""Regression checks for updating an already published HTML edition.

Run with: python3 -m unittest discover -s html/tools -p 'test_seo.py'
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
import seo


class SeoRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gql-seo-test-')
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        for path in seo.SITE.glob('*.html'):
            shutil.copy2(path, self.site / path.name)
        (self.site / 'assets').mkdir()
        shutil.copy2(seo.SITE / 'assets/search-index.js', self.site / 'assets/search-index.js')

    def document(self, filename):
        return BeautifulSoup((self.site / filename).read_text(), 'html.parser')

    def set_robots(self, filename, name, content):
        path = self.site / filename
        soup = self.document(filename)
        for tag in seo.robots_tags(soup):
            tag.decompose()
        soup.head.append(soup.new_tag('meta', attrs={'name': name, 'content': content}))
        path.write_text(str(soup))

    def sitemap(self):
        return {tag.text for tag in ET.parse(self.site / 'sitemap.xml').findall('.//{*}loc')}

    def test_refreshes_homepage_after_renaming_and_adding_guides(self):
        with patch.dict(seo.META), patch.dict(seo.GUIDES):
            filename = 'gql-tutorial.html'
            title = 'Updated GQL tutorial title'
            seo.META[filename] = (title, seo.META[filename][1])
            seo.guide('gql-extra-guide', 'Extra GQL guide', 'An extra guide.', '<p>Extra guide content.</p>')
            seo.apply(self.site)
            home = self.document('index.html')
            self.assertEqual(home.select_one('#learn-gql a[href="gql-tutorial.html"]').text, title)
            self.assertEqual(self.document(filename).h1.text, title)
            self.assertIsNotNone(home.select_one('#learn-gql a[href="gql-extra-guide.html"]'))
            self.assertEqual(len(home.select('#learn-gql')), 1)
            self.assertIn(seo.BASE + 'gql-extra-guide.html', self.sitemap())
            search = json.loads((self.site / 'assets/search-index.js').read_text()
                                .removeprefix('window.BOOK_SEARCH = ').strip().removesuffix(';'))
            self.assertEqual(sum(entry['url'] == 'gql-extra-guide.html' for entry in search), 1)

    def test_preserves_noindex_in_chapters_and_regenerated_guides(self):
        cases = [
            ('acknowledgments.html', 'robots', 'NOINDEX, nofollow'),
            ('book-overview.html', 'robots', 'none'),
            ('what-is-gql.html', 'robots', 'noindex,follow'),
            ('gql-tutorial.html', 'Googlebot', 'noindex'),
        ]
        for filename, name, content in cases:
            self.set_robots(filename, name, content)
        seo.apply(self.site)
        seo.apply(self.site)
        urls = self.sitemap()
        for filename, name, content in cases:
            with self.subTest(filename=filename):
                tags = seo.robots_tags(self.document(filename))
                self.assertEqual([(tag['name'], tag['content']) for tag in tags], [(name, content)])
                self.assertNotIn(seo.BASE + filename, urls)
        self.assertIn(seo.BASE + '04-gql-by-example.html', urls)

    def test_guides_do_not_inherit_homepage_noindex(self):
        self.set_robots('index.html', 'robots', 'noindex')
        with patch.dict(seo.META), patch.dict(seo.GUIDES):
            seo.guide('gql-extra-guide', 'Extra GQL guide', 'An extra guide.', '<p>Extra guide content.</p>')
            seo.apply(self.site)
            urls = self.sitemap()
            self.assertNotIn(seo.BASE, urls)
            for filename in seo.GUIDES:
                with self.subTest(filename=filename):
                    self.assertEqual(seo.robots_tags(self.document(filename)), [])
                    self.assertIn(seo.BASE + filename, urls)

    def test_rerun_is_stable_and_preserves_book_articles(self):
        before = {path.name: str(self.document(path.name).select_one('article'))
                  for path in self.site.glob('[0-9][0-9]-*.html')}
        seo.apply(self.site)
        paths = [*self.site.glob('*.html'), self.site / 'sitemap.xml', self.site / 'assets/search-index.js']
        first = {path: path.read_bytes() for path in paths}
        seo.apply(self.site)
        self.assertEqual(first, {path: path.read_bytes() for path in paths})
        for filename, article in before.items():
            with self.subTest(filename=filename):
                self.assertEqual(str(self.document(filename).select_one('article')), article)
        for filename in ('footnote-6.html', 'footnote-17.html'):
            tags = seo.robots_tags(self.document(filename))
            self.assertEqual(len(tags), 1)
            self.assertEqual(tags[0]['content'], 'noindex,follow')
            self.assertNotIn(seo.BASE + filename, self.sitemap())


if __name__ == '__main__':
    unittest.main()
