# coding: utf-8
'''
    程序通过输入url，下载并解析js动态加载的微信文章，返回结构化结果。
    被html_download取代。

    author: hiber_niu@163.com  date: 20150718
'''

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import etree
from io import StringIO, BytesIO
import html2text
import re

#Take this class for granted.Just use result of rendering.
class Render(QWebPage):
    def __init__(self, url):
      self.app = QApplication(sys.argv)
      QWebPage.__init__(self)
      self.loadFinished.connect(self._loadFinished)
      self.mainFrame().load(QUrl(url))
      self.app.exec_()

    def _loadFinished(self, result):
        self.frame = self.mainFrame()
        self.app.quit()


def article_extractor(url):
    r = Render(url)
    article = {}

    result = r.frame.toHtml()
    # This step is important.Converting QString to Ascii for lxml to process
    html_unicode = unicode(result.toUtf8(), encoding="utf-8")
    html = StringIO(html_unicode)

    content = html2text.html2text(html_unicode)
    sub_content = re.sub(r'!\[\]\(data[^)]*\)', '', content)

    htmlparser = etree.HTMLParser(encoding="utf-8")
    tree = etree.parse(html, htmlparser)
    title = tree.xpath(u'//*[@id="activity-name"]')
    date = tree.xpath(u'//*[@id="post-date"]')

    article['title'] = title[0].text.strip()
    article['date'] = date[0].text
    article['content'] = sub_content
    return article
