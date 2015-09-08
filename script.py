#!usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jayin'

import requests
import re
import codecs
import os
from bs4 import BeautifulSoup

url = u'http://weixin.sogou.com/weixin?query=育儿宝典&type=2&page={page}&ie=utf8'

articles = []


class Article(object):
    def __init__(self, title, url, img_url):
        self.title = title
        self.img_url = img_url
        self.url = url


def get_page(page=1):
    r = requests.get(url.format(page=page))
    return r.content


def filter_article(a):
    f = [
        u'有奖', u'有奖活动', u'免费'
    ]
    for x in f:
        if x in a.title:
            return True


def dump_file(articles):
    string = ''
    for a in articles:
        string += '%s %s %s\n' % (a.title, a.url, a.img_url)
    with codecs.open('data.txt', mode='wa', encoding='utf-8') as f:
        f.write(string.rstrip('\n'))


def work(page):
    soup = BeautifulSoup(get_page(page))
    _all = soup.find_all('a', attrs={'target': '_blank', 'href': re.compile('http://mp.weixin.qq.com')})

    length = len(_all)

    for x in xrange(0, length - 3, 2):
        img_url = _all[x].find('img').attrs['src'].split('&')[1].split('=')[1]
        title = _all[x + 1].text
        url = _all[x + 1]['href']
        a = Article(title, url, img_url)
        if not filter_article(a):
            articles.append(a)

    print('page %d is done' % page)


def main(start, stop):
    os.system('rm data.txt')
    for page in xrange(start, stop):
        work(page)
    dump_file(articles)


if __name__ == '__main__':
    main(2, 102)
