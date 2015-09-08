# coding: utf-8
'''
    程序通过输入url，下载并解析js动态加载的微信文章，返回结构化结果。

    author: hiber_niu@163.com  date: 20150718
'''

from lxml import etree
from io import StringIO
import html2text
from lxml import html
import re
import requests
from bs4 import BeautifulSoup

def article_extractor(url):
    article = {}

    r = requests.get(url, headers={'User-Agent': 'firefox'})
    source = r.text
    tree = html.fromstring(source)

    imgs = []
    m = re.search(r'var cover = "([^"]+)";', source)
    if m:
        cover =m.group(1)
        imgs.append(cover)
    soup = BeautifulSoup(source, 'lxml')
    for imgtag in soup.find_all('img'):
        if 'data-src' in imgtag.attrs:
            imgs.append(imgtag['data-src'])

    content = html2text.html2text(source)
    sub_content = re.sub(r'!\[\]\(data[^)]*\)', '', content)

    title = tree.xpath(u'//*[@id="activity-name"]')
    publisher = tree.xpath(u'//*[@id="img-content"]/div[1]/span')
    # date already extracted
    # date = tree.xpath(u'//*[@id="post-date"]')

    article['title'] = title[0].text.strip()
    article['publisher'] = publisher[0].text.strip()
    # article['date'] = date[0].text
    article['content'] = sub_content
    article['imgs'] = imgs
    return article

if __name__ == '__main__':
    url = u'http://mp.weixin.qq.com/s?__biz=Mjc1NjM3MjY2MA==&mid=221004900&idx=4&sn=5d414576abf7a1b38c0457e23578993a&3rd=MzA3MDU4NTYzMw==&scene=6#rd'
    article_extractor(url)
