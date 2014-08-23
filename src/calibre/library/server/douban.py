#!/usr/bin/python2.7
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2014, Rex Liao <talebook@foxmail.com>'
__docformat__ = 'restructuredtext en'

import datetime, json, logging, re

from calibre.utils.magick.draw import Image
from urllib import urlopen
from cStringIO import StringIO
from calibre.ebooks.metadata.book.base import Metadata

REMOVES = [
        re.compile(u'^\([^)]*\)\s*'),
        re.compile(u'^\[[^\]]*\]\s*'),
        re.compile(u'^【[^】]*】\s*'),
        re.compile(u'^（[^）]*）\s*')
        ]
class DoubanBookApi(object):

    def get_book_by_isbn(self, isbn):
        API_SEARCH = "https://api.douban.com/v2/book/isbn/%s?apikey=04f64a310943d5d80ee2de931bcb8188"
        API_SEARCH = "https://api.douban.com/v2/book/isbn/%s?apikey=0f3f80e12f8f119a2dbe82a38ead34ce"
        API_SEARCH = "https://api.douban.com/v2/book/isbn/%s?apikey=05d8205c45d62eb011886114d1828c10"
        url = API_SEARCH % isbn
        rsp = json.loads(urlopen(url).read())
        if 'code' in rsp and rsp['code'] != 0:
            logging.error("******** douban API error: %d-%s **********" % (rsp['code'], rsp['msg']) )
            return None
        return rsp

    def get_book_by_title(self, title):
        API_SEARCH = "https://api.douban.com/v2/book/search?apikey=052c9ac15e9870500f85d0441bc950f0&q=%s"
        url = API_SEARCH % (title.encode('UTF-8'))
        rsp = json.loads(urlopen(url).read())
        if 'code' in rsp and rsp['code'] != 0:
            logging.error("******** douban API error: %d-%s **********" % (rsp['code'], rsp['msg']) )
            return None

        books = rsp['books']
        for b in books:
            if b['title'] == title:
                return b
        return books[0]

    def str2date(self, s):
        for fmt in ("%Y-%m-%d", "%Y-%m"):
            try:
                return datetime.datetime.strptime(s, fmt)
            except:
                continue
        return None

    def get_metadata(self, md):
        book = None
        if md.isbn:
            book = self.get_book_by_isbn(md.isbn)
        if not book:
            book = self.get_book_by_title(md.title)
        mi = Metadata(book['title'])
        mi.authors     = book['author']
        mi.author_sort = mi.authors[0] if mi.authors else None
        if mi.author_sort:
            for r in REMOVES:
                mi.author_sort = r.sub("", mi.author_sort)
            mi.authors[0] = mi.author_sort
        mi.publisher   = book['publisher']
        mi.comments    = book['summary']
        mi.isbn        = book.get('isbn13', None)
        mi.tags        = [ t['name'] for t in book['tags'] ][:8]
        mi.rating      = int(float(book['rating']['average']))
        mi.pubdate     = self.str2date(book['pubdate'])
        mi.timestamp   = datetime.datetime.now()
        mi.douban_id   = book['id']
        mi.douban_author_intro = book['author_intro']
        mi.douban_subtitle = book.get('subtitle', None)

        img_url = book['images']['large']
        img_fmt = img_url.split(".")[-1]
        img = StringIO(urlopen(img_url).read())
        mi.cover_data = (img_fmt, img)
        logging.error("=================\ndouban metadata:\n%s" % mi)
        return mi

def get_douban_metadata(mi):
    api = DoubanBookApi()
    try:
        return api.get_metadata(mi)
    except Exception as e:
        import traceback
        logging.error(traceback.format_exc())
        return None


