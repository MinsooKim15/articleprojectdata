# 1.기존 DB에서 DATA를 꺼낸다. getArticle
# 2. TF-IDF를 때린다. vectorizeByTFIDF
# 3. Clutser의 개수를 구한다. numberOfCluster
# 4. Clustering을 한다. clusterByHAC
# 5. Clustering 결과를 새로운 DB에 저장한다. clusterToDB
# 6. 원본 DB에도 저장을 해야할까? 둘 다 clusterToDB

import pandas as pd
import pandas as pd
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql
import json
import datetime


class TopicCluster():
    articleData = pd.DataFrame()
    tfidfFrame = pd.DataFrame()
    #미리 자료형을 알아야 할 것 같은데.. 통 모르겠어
    # tfidf = 0

    def __init__(self):
        #이렇게 아무 것도 안 할 때에는 뭐라고 써야 하지 모르곘네 ㅜ
        with open('config.json') as json_data_file:
            data0 = json.load(json_data_file)
        self.dbHost = data0['mysql']['host']
        self.dbId = data0['mysql']['id']
        self.pw = data0['mysql']['pw']
        self.db = data0['mysql']['db']
        print("YES!")

    def getArticle(self,source):
        if source == "file":
            self.articleData = pd.read_csv('./temp/sample3.csv', encoding= 'utf-8', header= 0)
                    #비어 있는 articleData는 싫어요!.! -> 나중에는 SQL 단계에서 삭제하자
        else:
            #일단은 현재의 파일을 잘 읽어 온다.(뒤의 파이프라인이 잘 흘러 내려 가는 것이 먼저 이기 때문, 이 후에 DB에서 직접 가져오자)
            conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
            # cursor = conn.cursor()
            sql = "select * from article WHERE article_body IS NOT NULL"
            self.articleData = pd.read_sql(sql, con = conn)
            # print("sql start")
            # sql = "select * from `article` where `companyName` = '경향'"
            # flattened_values = [item for sublist in values_to_insert for item in sublist]
            # print(flattened_va

            #MYSQL에서 잘 가져와도 일단은 두자..
            self.articleData = self.articleData.dropna(subset=["article_body"])

        #요것이 결론
        #특정한 조건에 따라서 MYSQL에서 Data를 뽑아서, Pandas DataFrame에 담아 둔다.
        # print(self.articleData["article_body"])

    # def tokenizer_noun(doc):
    #     return twitter.nouns(doc)
    #
    # def tokenizer_morphs(doc):
    #     return twitter.morphs(doc)
    def twitter_vectorizer(self,list):
        from konlpy.tag import Kkma
        kkma = Kkma()
        from konlpy.tag import Twitter
        twitter = Twitter()
        # a = []
        # for i in list:
            # a = a + twitter.nouns(i)
        return(twitter.nouns(list))

    def vectorizeByTFIDF(self):
        #전 처리(정리)
        #왜인지 '\n'들이 제거 안 된 것들이 많이 남아있음.
        articleList = self.articleData[['article_body']].dropna().values
        new_articleList = []
        for i in articleList:
            article = ""
            for k in i:
                article = article + k
            article.rstrip('\n')
            article.replace('\n', '')
            article = article.encode('utf-8').decode('utf-8')
            new_articleList.append(article)
            new_articleArray = np.array(new_articleList)
        # print(new_articleList)

        # print(repr(unicode(an)))
        # an = repr(unicode(an))
        # an = codecs.decode(an, 'unicode_escape')
        tfidf = TfidfVectorizer(tokenizer=self.twitter_vectorizer,max_features = 1000, max_df=0.95, min_df=0)
        # print(tfidf)
        #generate tf-idf term-document matrix
        A_tfidf_sp = tfidf.fit_transform(new_articleList)  #size D x V

        tfidf_dict = tfidf.get_feature_names()
        # print(tfidf_dict)
        data_array = A_tfidf_sp.toarray()
        self.tfidfFrame = pd.DataFrame(data_array, columns=tfidf_dict)

    def numberOfCluster(self):

        #일단 기본 값으로 10을 넣는다. 이건 더 실험해보고 넣자
        self.n_clusters = 10

    def clusterByHAC(self):
        from sklearn.cluster import AgglomerativeClustering
        self.numberOfCluster()
        cluster = AgglomerativeClustering(n_clusters=self.n_clusters, affinity='euclidean', linkage='ward')
        topic = cluster.fit_predict(self.tfidfFrame)
        self.articleData["topic"] = topic

    def makeTopicId(self,topicNumber):
        currentTime = datetime.datetime.now()
        year = str(currentTime.year)
        if currentTime.month < 10 :
            month = "0" + str(currentTime.month)
        else :
            month = str(currentTime.month)
        if currentTime.day < 10 :
            day = "0" + str(currentTime.day)
        else:
            day  = str(currentTime.day)
        if currentTime.hour < 10 :
            hour = "0" + str(currentTime.hour)
        else:
            hour = str(currentTime.hour)
        if currentTime.minute < 10 :
            minute = "0" + str(currentTime.minute)
        else:
            minute = str(currentTime.minute)
        if currentTime.second < 10 :
            second = "0" + str(currentTime.second)
        else :
            second = str(currentTime.second)
        newId  = "topic_"+str(topicNumber)+"_"+ year+ month + day + hour + minute + second
        return newId

    def clusterToDB(self):
        #1. articleData는 "TopicId" 칼럼을 갖게 된다.
        self.articleData["topicId"] = (self.articleData["topic"]).apply(self.makeTopicId)
        #2. TopicData로 "TopicID" 정보만을 모은 DB를 만든다.
        groupedData = self.articleData.groupby('topicId').count()
        topicData = pd.DataFrame()
        topicData["count"] = groupedData["id"]
        topicData.index.name = 'topicId'
        topicData.reset_index(inplace=True)
        topicData["clusteredTime"] = topicData["topicId"].apply(lambda x: x[8:])
        #3. article Tabledp "topicID" 칼럼을 업데이트한다.
        titleIdList = self.articleData["titleId"].tolist()
        topicIdList = self.articleData["topicId"].tolist()
        mysqlList = []
        for key, value in enumerate(titleIdList):
            a = (topicIdList[key], titleIdList[key])
            mysqlList.append(a)
        print(mysqlList)
        conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
        cursor = conn.cursor()
        try:
            with conn.cursor() as cursor:
                print("sql start")
                sql = "UPDATE article SET topicId = %s WHERE titleId = %s"
                print(sql)
                # flattened_values = [item for sublist in values_to_insert for item in sublist]
                # print(flattened_values)
                cursor.executemany(sql, mysqlList)
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
        #4. topic Table에 신규 Row를 추가한다.
        timeList = topicData["clusteredTime"].tolist()
        idList = topicData["topicId"].tolist()
        countList = topicData["count"].tolist()
        values_to_insert = []
        conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
        cursor = conn.cursor()
        for key,value in enumerate(timeList):
            values_to_insert.append((timeList[key], idList[key], countList[key]))
            # # print(file_article_write_time)
            # print(file_author)
        try:
            with conn.cursor() as cursor:
                print("sql start")
                sql = "INSERT INTO topics (clusteredTime, topicId, articleCount) VALUES " + ",".join("(%s,%s,%s)" for _ in values_to_insert)
                print(sql)
                flattened_values = [item for sublist in values_to_insert for item in sublist]
                # print(flattened_values)
                cursor.execute(sql, flattened_values)
            conn.commit()
            print(cursor.lastrowid)
        except Exception as except_detail:
            print("pymysql.err.ProgrammingError: «{}»".format(except_detail))
        finally:
            conn.close()
            print("good")
            return True

if __name__ == "__main__":
    # execute only if run as a script
    topicCluster = TopicCluster()
    topicCluster.getArticle(source="SQL")
    topicCluster.vectorizeByTFIDF()
    topicCluster.clusterByHAC()
    topicCluster.clusterToDB()
    # print(topicCluster.articleData[["article_body","topic"]])
