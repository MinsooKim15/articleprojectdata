# 1.기존 DB에서 DATA를 꺼낸다. getArticle
# 2. TF-IDF를 때린다. vectorizeByTFIDF
# 3. Clutser의 개수를 구한다. numberOfCluster
# 4. Clustering을 한다. clusterByHAC
# 5. Clustering 결과를 새로운 DB에 저장한다. clusterToDB
# 6. 원본 DB에도 저장을 해야할까? ?

import pandas as pd

class TopicCluster():
    articleData = pd.DataFrame()
    def getArticle(self):

        #요것이 결론
        #특정한 조건에 따라서 MYSQL에서 Data를 뽑아서, Pandas DataFrame에 담아 둔다.
        self.articleData = pd.DataFrame()

    def vectorizeByTFIDF(self):
        

TopicCluster()
