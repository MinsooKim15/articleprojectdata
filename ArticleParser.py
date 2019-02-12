import requests
import justext
from bs4 import BeautifulSoup
import re
import newspaper
import json
def something():
    with open('all.json') as json_data_file:
        data0 = json.load(json_data_file)
    for i in data0:
        url = data0[i][0]['links'][0]['href']
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        # url = "http://news.khan.co.kr/kh_news/khan_art_view.html?artid=201901300748001&code=970100&utm_campaign=rss_btn_click&utm_source=khan_rss&utm_medium=rss&utm_content=total_news"
        response = session.get(url)
        html = response.content
        # # paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
        #
        article = newspaper.Article('')
        article.set_html(html)
        article.parse()
        print("******************")
        print(i)
        print(article.title)
        print(article.authors)
        print(article.text)

class ArticleParser:
    url_list = []
    def __init__(self):
        #객체화하는 걸 완전 잊었다.... 그렇게 하는 거였지..
        with open('config.json') as json_data_file:
            data0 = json.load(json_data_file)

        self.dbHost = data0['mysql']['host']
        self.dbId = data0['mysql']['id']
        self.pw = data0['mysql']['pw']
        self.db = data0['mysql']['db']
    def get_article_list(self):
        import pymysql
        conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
        cursor = conn.cursor()
        print("sql start")
        sql = "select * from article"
        print(sql)
        # flattened_values = [item for sublist in values_to_insert for item in sublist]
        # print(flattened_values)
        try:
            cursor.execute(sql)
            records = cursor.fetchall()
            for row in records:
                self.url_list.append(row[3])
            conn.commit()
            # print(cursor.lastrowid)
        except Exception as except_detail:
            print("pymysql.err.ProgrammingError: «{}»".format(except_detail))
        finally:
            conn.close()
            print("good")
            return True
    def parse(self):
        for i in self.url_list:
            url = i
            # url = self.url_list
            session = requests.Session()
            session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
            # url = "http://news.khan.co.kr/kh_news/khan_art_view.html?artid=201901300748001&code=970100&utm_campaign=rss_btn_click&utm_source=khan_rss&utm_medium=rss&utm_content=total_news"
            response = session.get(url)
            html = response.content
            # # paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
            #
            article = newspaper.Article('')
            article.set_html(html)
            article.parse()
            print("******************")
            print(article.title)
            print(article.authors)
            print(article.text)

if __name__ == "__main__":
    articleParser = ArticleParser()
    articleParser.get_article_list()
    print(articleParser.url_list)
    articleParser.parse()
