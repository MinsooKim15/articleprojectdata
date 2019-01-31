# Atom의 콘솔창은 한글 결과가 제대로 안 나온다. 반드시 터미널로 확인하자
# 대충 구조는 비슷한 것 같다.
import feedparser
import json
from pprint import pprint


# print(data)
# if(d[])
# url = "http://www.huffingtonpost.kr/feeds/verticals/korea/news.xml"
# url = data["items"][0]['rss_url']["all"]


# TODO : HealthChecker
# TODO : MYSQL 입력기
# 근데 Class에서 Dependency가 있으면 어떻게하지

#RSSConnecter : RSS JSON 파일 읽어옴, RSS 호출 1) 결과를 뱉음, 2) Health Check를 함.
class RssConnector:
    def __init__(self):
        #객체화하는 걸 완전 잊었다.... 그렇게 하는 거였지..
        with open('config.json') as json_data_file:
            data0 = json.load(json_data_file)
        self.onlyCompany = data0['rss']['onlyCompanyInFilter']
        self.company = data0['rss']['companyToFilter']
        self.jsonConfig = data0['rss']['urlFile']
        self.healthConfig = data0['rss']['healthFile']
        self.dbHost = data0['mysql']['host']
        self.dbId = data0['mysql']['id']
        self.pw = data0['mysql']['pw']
        self.db = data0['mysql']['db']

        #Initialization 정의

    def connector(self):
        result = {}
        healthCheckResult = {}
        print(self.onlyCompany,bool)
        with open(self.jsonConfig,"rt", encoding= "utf-8") as f:
            data = json.load(f)
        for i in range(len(data["items"])):
            url = data["items"][i]['rss_url']["all"]
            d = feedparser.parse(url)
            companyName = data['items'][i]['company']
            if self.onlyCompany == "True":
                for k in self.company:
                    if k == companyName :
                        if (len(d['entries']) != 0):
                            result.update({data['items'][i]['company']:d['entries']})
                            healthCheckResult.update({companyName: True})
                        else:
                            healthCheckResult.update({companyName: False})
            else:
                if (len(d['entries']) != 0):
                    result.update({data['items'][i]['company']:d['entries']})
                    healthCheckResult.update({companyName: True})
                else:
                    healthCheckResult.update({companyName: False})
        return (result, healthCheckResult)

    def healthChecker(self, result):
        # typechecking
        if isinstance(result, dict):
            import json
            # a = json.dumps(result, ensure_ascii=False).encode('utf8')
            with open(self.healthConfig, 'w') as fp:
                json.dump(result, fp, ensure_ascii=False)
                # json.dump(result, fp, ensure_ascii=False, encoding='utf8')
        else:
            print("This is not dictionary!!")

    #Parsing된 데이터 열을 넣어주면, MySql로 넣고 끝나면 True를 뱉는다.
    def dataToMysql(self, data):
        # 기사 작성 시간은 string format으로 함 -> 나중에 다듬자
        import pymysql
        conn = pymysql.connect(host= self.dbHost, user = self.dbId, password = self.pw, db = self.db, charset='utf8')
        curs = conn.cursor()
        values_to_insert = []
        for i in data:
    # 고른 언론사 중 특정한..
            for k in data[i]:
                file_title = k["title"]
                file_summary = k["summary"]
                file_link = k["link"]
                file_article_write_time = k["updated"]
                # file_article_write_time = datetime.strptime(file_article_write_time, '%Y-%m-%d %H:%M:%S')
                file_author = k["author"]
                values_to_insert.append((file_title,file_summary,file_link,file_article_write_time,file_author))
                # # print(file_article_write_time)
                # print(file_author)
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO article (title, summary, link, article_write_time, author) VALUES " + ",".join("(%s,%s,%s,%s,%s)" for _ in values_to_insert)
                flattened_values = [item for sublist in values_to_insert for item in sublist]
                print(flattened_values)
                cursor.execute(sql, flattened_values)
            conn.commit()
            print(cursor.lastrowid)
        finally:
            conn.close()
            print("good")
            return True



if __name__ == "__main__":
    rssConnector = RssConnector()
    result, healthCheckResult= rssConnector.connector()
    # print(result)
    rssConnector.dataToMysql(result)
    # rssConnector.healthChecker(healthCheckResult)
    # with open('./temp5.json','w') as fp:
    #     json.dump(result, fp, ensure_ascii=False)
    # print("done")
