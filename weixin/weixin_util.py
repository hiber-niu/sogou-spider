#!usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Using this program to download weixin search results.
    Providing two methods:
        get_service_search_page: using weixin service openid to search
        get_article_search_page: using keywords to search

    author: hiber_niu@163.com   date:2015-07-03
'''
__author__ = 'hiber'

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import dateparser
from selenium.webdriver.common.keys import Keys

from datetime import datetime, timedelta

from pymongo import MongoClient
# import requests
import re
import csv
import collections


def get_service_search_page(openid, service_name, pages=2):
    service_url = u'http://weixin.sogou.com/weixin?type=1&query={service_name}'
    driver = webdriver.Chrome('D:/chromedriver')
    articles = []

    driver.get(service_url.format(service_name=service_name))
    service_redirect = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sogou_vr_11002301_box_0"]/div[2]/h3')))
    service_redirect.click()

    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
    driver.implicitly_wait(1)
    driver.switch_to.window(driver.window_handles[-1])
    # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL +'W')
    print driver.current_url

    click_num = 0

    try:
        if click_num < pages:
            click_more = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="wxmore"]/a')))
            click_more.click()
            click_num = click_num + 1

        # waitting until element is already reloaded
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="wxmore"]/a')))

        for i in range(pages*10):
            index = str(i)
            article = collections.OrderedDict()
            publish_date = date_parse(driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_box_'+index+'"]/div[2]/div').text)
            if not publish_date:
                continue

            article['publish_date'] = publish_date
            article['service_name'] = service_name
            article['title'] = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_title_'+index+'"]').text
            article['article_url'] = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_title_'+index+'"]').get_attribute('href')
            article['summary'] = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_summary_'+index+'"]').text
            article['openid'] = openid
            article['url'] = driver.current_url
            # article['url'] = service_url.format(openid=openid)
            article['crawled_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # article['html'] = requests.get(article['article_url']).content
            articles.append(article)


# 搜狗修改了网页代码 20150812 之前可用
        # title_list = driver.find_elements_by_xpath('//*[@id="sogou_vr_11002601_box_0"]/div[2]/h4')
        # summary_list = driver.find_elements_by_xpath('//*[@id="sogou_vr_11002601_box_0"]/div[2]/p[1]')
        # article_url_list= driver.find_elements_by_xpath('//*[@id="sogou_vr_11002601_img_0"]')
        # publish_date_list = driver.find_elements_by_xpath('//*[@id="sogou_vr_11002601_box_0"]/div[2]/p[2]')

        # for title, summary, article_url, publish_date in zip(title_list, summary_list, article_url_list, publish_date_list):
            # article = {}
            # article['openid'] = openid
            # article['service_name'] = service_name
            # article['url'] = service_url.format(openid=openid)
            # article['title'] = title.text
            # article['summary'] = summary.text
            # article['article_url'] = article_url.get_attribute('href')
            # article['publish_date'] = date_parse(publish_date.text)
            # article['crawled_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # # article['html'] = requests.get(article['article_url']).content
            # articles.append(article)

    except Exception:
        driver.close()
        raise
    finally:
        # 搜狗修改了网页跳转逻辑，必须在当前session内跳转才能获得微信文章真实网
        # 址。20150908
        for index in range(len(articles)):
            try:
                driver.get(articles[index]['article_url'])
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="activity-name"]')))
                articles[index]['article_url'] = driver.current_url
            except Exception:
                continue

        driver.quit()
    return articles


def get_keyword_search_page(query, pages=2):
    url = u'http://weixin.sogou.com/weixin?query={query}&type=2&page={page}&ie=utf8'
    driver = webdriver.Chrome('D:/chromedriver')

    driver.get(url.format(query=query.decode('utf-8'), page=1))
    articles = []

    # os.environ['DISPLAY'] = None
    page = 1
    try:
        while True:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sogou_next"]')))

            for i in range(8):
                article = collections.OrderedDict()
                try:
                    publish_text = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_box_'+str(i)+'"]/div[2]/div').text
                    # split publish_text with two continuous number
                    match = re.match(r'(.*?)(\d\d.+)', publish_text)
                    if not date_parse(match.group(2)):
                        continue
                    article['publish_date'] = date_parse(match.group(2))
                    article['publisher'] = match.group(1)
                    article['title'] = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_title_'+str(i)+'"]').text
                    article['article_url'] = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_img_'+str(i)+'"]').get_attribute('href')
                    article['summary'] = driver.find_element_by_xpath('//*[@id="sogou_vr_11002601_summary_'+str(i)+'"]').text
                    article['query_word'] = query
                    article['url'] = url.format(query=query.decode('utf-8'), page=page)
                    article['crawled_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    # article['html'] = requests.get(article['article_url']).content
                    articles.append(article)
                except Exception as e:
                    print(str(e))
                    continue
            # crawl next page
            page = page + 1
            if page > pages:
                break
            next_page = driver.find_element_by_xpath('//*[@id="sogou_next"]')
            next_page.click()
    except Exception:
        driver.close()
        raise
    finally:
        for index in range(len(articles)):
            try:
                driver.get(articles[index]['article_url'])
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="activity-name"]')))
                articles[index]['article_url'] = driver.current_url
            except Exception:
                raise

        driver.quit()

    return articles


def date_parse(date_str):
    '''
    Parse chinese date and time. If success return parsed date and time, else
    return input date_str.
    '''
    date_text = date_str.replace(u'月', ',').replace(u'日', ',')
    if u'年' in date_text:
        date_text = date_text.replace(u'年', ',')
    else:
        date_text = time.strftime('%Y',time.localtime(time.time())) +',' + date_text
    result = dateparser.parse(date_text, date_formats=['%Y-%m-%d %H:%M:%S'])

    if result:
        if (datetime.now()-result) > timedelta(days=2):
            return False
    else:
        return False

    if result:
        return str(result)
    else:
        return date_str


# mongodb utility
def article_to_mongodb(database, collection, articles,
                       host='localhost', port=27017):
    '''
    # store stock information into database.collection.
    # jsonData is stock information
    '''
    client = MongoClient(host, port)
    db = client[database]
    coll = db[collection]

    out_articles = articles[:]
    for article in articles:
        # find and remove duplicate document
        find_cur = coll.find({'title': article['title'],
                              'publish_date': {'$eq': article['publish_date']}})
        if find_cur.count() > 0:
            out_articles.remove(article)

    for article in articles:
        # 查询标题一致，时间较老的信息。
        coll.update({'title': article['title'], 'publish_date': {'$lte': article['publish_date']}},
                    article,
                    upsert=True)

    return out_articles


# remove duplicaiton
def remove_dup(articles):
    # 按标题去重，相同的保留最新文章
    temp_dict = {}
    for article in articles:
        if article['title'] not in temp_dict:
            temp_dict[article['title']] = article
        else:
            if article['publish_date'] > temp_dict[article['title']]['publish_date']:
                articles.remove(temp_dict[article['title']])
                temp_dict[article['title']] = article

    return articles


def article_to_file(prefix, articles):
    '''
    store articles to csv file, using '$' as delimiter
    '''
    file_name = 'output/'+prefix+time.strftime('%Y%m%d')+'.csv'

    with open(file_name, 'wb') as f:
        if len(articles) == 0:
            f.write('庞大鳄，今天没有新数据!')
            return
        keys = articles[0].keys()
        dict_writer = csv.DictWriter(f, fieldnames=keys, delimiter="$")
        dict_writer.writeheader()
        dict_writer.writerows(articles)


# def article_to_file(prefix, articles):
    '''
    store articles to json file
    '''
    # file_name = 'output/'+prefix+time.strftime('%Y%m%d')+'.json'
    # import json
    # with open(file_name, 'wb') as f:
        # json.dump(articles, f, ensure_ascii=False, indent=2)


# if __name__ == '__main__':
    # main(2, 5)
    # get_article_search_page(start=1, end=3)
#     get_service_search_page(['oIWsFt8iOH_akAg1vJ56tk8wZZcQ'], pages=2)
