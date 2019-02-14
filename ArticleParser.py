import requests
import justext
from bs4 import BeautifulSoup
import re
import newspaper
import json
import pymysql

class ArticleParser:
    url_list = []
    article_list = []
    def __init__(self):
        #객체화하는 걸 완전 잊었다.... 그렇게 하는 거였지..
        with open('config.json') as json_data_file:
            data0 = json.load(json_data_file)

        self.dbHost = data0['mysql']['host']
        self.dbId = data0['mysql']['id']
        self.pw = data0['mysql']['pw']
        self.db = data0['mysql']['db']
    def get_article_list(self):

        conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
        cursor = conn.cursor()
        print("sql start")
        # sql = "select * from article"
        sql = "select * from `article` where `companyName` = '경향'"
        print(sql)
        # flattened_values = [item for sublist in values_to_insert for item in sublist]
        # print(flattened_values)
        try:
            cursor.execute(sql)
            records = cursor.fetchall()
            for row in records:
                a = (row[12],row[3])
                self.url_list.append(a)
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
            url = i[1]
            # url = self.url_list
            session = requests.Session()
            session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
            # url = "http://news.khan.co.kr/kh_news/khan_art_view.html?artid=201901300748001&code=970100&utm_campaign=rss_btn_click&utm_source=khan_rss&utm_medium=rss&utm_content=total_news"
            response = session.get(url)
            html = response.content
            # # paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
            article = newspaper.Article('')
            article.set_html(html)
            article.parse()
            a = (article.text,i[0])
            self.article_list.append(a)
            print("parse Done")
    def saveToMysql(self):
        # 기사 작성 시간은 string format으로 함 -> 나중에 다듬자
        conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
        curs = conn.cursor()
        try:
            with conn.cursor() as cursor:
                print("sql start")
                sql = "UPDATE article SET article_body = %s WHERE titleId = %s"
                print(sql)
                # flattened_values = [item for sublist in values_to_insert for item in sublist]
                # print(flattened_values)
                cursor.executemany(sql, self.article_list)
                # print(cursor)
            conn.commit()
            print(cursor.lastrowid)
        except Exception as except_detail:
            print("pymysql.err.ProgrammingError: «{}»".format(except_detail))
        finally:
            #끝났으니 비우자. 그런데 곧 Mysql Update 잘 되었는지의 로직은 추가해야 할듯
            self.article_list = []
            conn.close()
            print("good")
            return True


if __name__ == "__main__":
    articleParser = ArticleParser()
    articleParser.get_article_list()
    articleParser.parse()
    articleParser.saveToMysql()
