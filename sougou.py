#!usr/bin/env python
# -*- coding: utf-8 -*-
'''
Using this program to download weixin search results.

author: hiber_niu@163.com   date:2015-07-03
'''
__author__ = 'hiber'

from weixin.weixin_util import get_keyword_search_page
from weixin.weixin_util import get_service_search_page
# from weixin.html_download import article_extractor
from weixin.weixin_util import article_to_mongodb
from weixin.weixin_util import article_to_file
from weixin.weixin_util import remove_dup
from weixin.email_result import send_email

import sys
import ConfigParser


def sougou():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    import uniout

    if len(sys.argv) > 2:
        print(' USAGE: [service/keywords]')
        return
    # read config parameter
    config = ConfigParser.ConfigParser()
    with open('conf/config.conf', 'r') as cfgfile:
        config.readfp(cfgfile)

    if len(sys.argv) == 2:
        if sys.argv[1] == 'keywords':
            keywords_file = config.get('keywords', 'file')
            get_keyword_search_results(keywords_file)
        elif sys.argv[1] == 'service':
            service_file = config.get('service', 'file')
            get_service_search_results(service_file)
    else:
        keywords_file = config.get('keywords', 'file')
        get_keyword_search_results(keywords_file)

        service_file = config.get('service', 'file')
        get_service_search_results(service_file)

    # send email.
    send_email()


def get_keyword_search_results(keywords_file):
    articles = []
    with open(keywords_file, 'r') as keywords:
        for line in keywords.readlines():
            line = line.strip()
            # 去除注释和空行
            if line.startswith('#') or len(line) == 0:
                continue
            query = line.split()

            # 对爬取出错的再尝试一次，两次出错放弃
            if len(query) == 1:
                try:
                    articles.extend(get_keyword_search_page(query[0]))
                except Exception as e:
                    print(str(e))
                    print('Exception occured, retried with %s' % query[0])
                    try:
                        articles.extend(get_keyword_search_page(query[0]))
                    except Exception as e:
                        print('%s Exception occured agagin!' % query[0])
                        continue

            elif len(query) == 2:
                try:
                    articles.extend(get_keyword_search_page(query[0], int(query[1])))
                except Exception as e:
                    print(str(e))
                    print('Exception occured, retried with %s' % query[0])
                    try:
                        articles.extend(get_keyword_search_page(query[0], int(query[1])))
                    except Exception as e:
                        print('%s Exception occured agagin!' % query[0])
                        continue

            else:
                print(line + u'：输入格式错误！')
                return

            '''
            for index, article in enumerate(articles):
                print('line 53, get html_info begin')
                try:
                    html_info = article_extractor(article['article_url'])
                    articles[index].update(html_info)
                except Exception, e:
                    print e
                    continue
                print('line 56, get html_info begin')
            '''
    articles = remove_dup(articles)
    # query mongodb and remove documnets already stored
    # articles = article_to_mongodb('weixin', 'sougou', articles)
    article_to_file('keywords', articles)


def get_service_search_results(service_file):
    articles = []
    with open(service_file, 'r') as services:
        for line in services.readlines():
            line = line.strip()
            # 去除注释和空行
            if line.startswith('#') or len(line) == 0:
                continue
            query = line.split()

            # 对爬取出错的再尝试一次，两次出错放弃
            if len(query) == 2:
                try:
                    articles.extend(get_service_search_page(query[0], query[1]))
                except Exception as e:
                    print('Exception occured, retried with %s' % query[1])
                    try:
                        articles.extend(get_service_search_page(query[0], query[1]))
                    except Exception as e:
                        print('%s Exception occured agagin!' % query[1])
                        continue

            elif len(query) == 3:
                try:
                    articles.extend(get_service_search_page(query[0], query[1], int(query[2])))
                except Exception as e:
                    print('Exception occured, retried with %s' % query[1])
                    try:
                        articles.extend(get_service_search_page(query[0], query[1], int(query[2])))
                    except Exception as e:
                        print('%s Exception occured agagin!' % query[1])
                        continue

            else:
                print(line + u'：输入格式错误！')
                return

            '''
            for article, index in enumerate(articles):
                try:

                    html_info = article_extractor(article['article_url'])
                    articles[index].update(html_info)
                except Exception, e:
                    print e
                    continue
            '''

    articles = remove_dup(articles)
    # query mongodb and remove documnets already stored
    # articles = article_to_mongodb('weixin', 'service', articles)
    article_to_file('service', articles)


if __name__ == '__main__':
    # import sched, time
    # s = sched.scheduler(time.time, time.sleep)
    # s.enter(86400, 0, sougou, ())
    # s.enter(300, 0, sougou, ())
    # s.run()
    sougou()
    # get_service_search_page(['oIWsFt8iOH_akAg1vJ56tk8wZZcQ'], pages=2)
