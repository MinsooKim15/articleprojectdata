# 1.기존 DB에서 DATA를 꺼낸다. getArticle
# 2. TF-IDF를 때린다. vectorizeByTFIDF
# 3. Clutser의 개수를 구한다. numberOfCluster
# 4. Clustering을 한다. clusterByHAC
# 5. Clustering 결과를 새로운 DB에 저장한다. clusterToDB
# 6. 원본 DB에도 저장을 해야할까? ?

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



class TopicCluster():
    articleData = pd.DataFrame()
    tfidfFrame = pd.DataFrame()
    #미리 자료형을 알아야 할 것 같은데.. 통 모르겠어
    # tfidf = 0

    def __init__(self):
        #이렇게 아무 것도 안 할 때에는 뭐라고 써야 하지 모르곘네 ㅜ
        print("YES!")
    def getArticle(self):
        #일단은 현재의 파일을 잘 읽어 온다.(뒤의 파이프라인이 잘 흘러 내려 가는 것이 먼저 이기 때문, 이 후에 DB에서 직접 가져오자)
        #요것이 결론
        #특정한 조건에 따라서 MYSQL에서 Data를 뽑아서, Pandas DataFrame에 담아 둔다.
        self.articleData = pd.read_csv('./temp/sample3.csv', encoding= 'utf-8', header= 0)
        #비어 있는 articleData는 싫어요!.! -> 나중에는 SQL 단계에서 삭제하자
        self.articleData = self.articleData.dropna(subset=["article_body"])
        # print(self.articleData["article_body"])

    # def tokenizer_noun(doc):
    #     return twitter.nouns(doc)
    #
    # def tokenizer_morphs(doc):
    #     return twitter.morphs(doc)


    def vectorizeByTFIDF(self):
        #전 처리(정리)
        #왜인지 '\n'들이 제거 안 된 것들이 많이 남아있음.
        articleList = self.articleData['article_body'].values
        new_articleList = []
        for i in articleList:
            article = ""
            for k in i:
                article = article + k
            article.rstrip('\n')
            article.replace('\n', '')
            new_articleList.append(article)
        print(new_articleList)
        from konlpy.tag import Kkma
        kkma = Kkma()
        print(kkma.nouns(new_articleList))
        # tfidf = TfidfVectorizer(tokenizer=twitter.nouns,max_features = 1000, max_df=0.95, min_df=0)
        #generate tf-idf term-document matrix
        # A_tfidf_sp = tfidf.fit_transform(new_articleList)  #size D x V
        # tfidf_dict = tfidf.get_feature_names()
        # data_array = A_tfidf_sp.toarray()
        # self.tfidfFrame = pd.DataFrame(data_array, columns=tfidf_dict)

    def numberOfCluster(self):

        #일단 기본 값으로 10을 넣는다. 이건 더 실험해보고 넣자
        return 10

    def clusterByHAC(self):
        from sklearn.cluster import AgglomerativeClustering
        cluster = AgglomerativeClustering(n_clusters=self.numberOfCluster, affinity='euclidean', linkage='ward')
        topic = cluster.fit_predict(self.tfidfFrame)
        self.articleData["topic"] = topic

    # def clusterToDB(self):
    #     return ?

if __name__ == "__main__":
    # execute only if run as a script
    topicCluster = TopicCluster()
    topicCluster.getArticle()
    topicCluster.vectorizeByTFIDF()
    # topicCluster.clusterByHAC()
    # print(topicCluster.articleData["article_body","topic"])
