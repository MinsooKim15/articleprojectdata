# Atom의 콘솔창은 한글 결과가 제대로 안 나온다. 반드시 터미널로 확인하자
# 대충 구조는 비슷한 것 같다.
import feedparser
import json
from pprint import pprint
from dateutil import parser
import hashlib



# print(data)
# if(d[])
# url = "http://www.huffingtonpost.kr/feeds/verticals/korea/news.xml"
# url = data["items"][0]['rss_url']["all"]


# TODO : HealthChecker
# TODO : Make Article ID
# TODO : Article ID CHECKER(중복제거기)
# TODO : Cover all the press Compnay
# TODO : Internet Connection Error 예외 정의
# TODO : 아직도 같은 ID가 있음 우쨔지 -> Title Id 만듬
# 정책 : 시간Id로 체크, 같은 것이 있으면 Title Id로 체크함.
# TODO : 객체화

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
            pressId = data['items'][i]['press_id']
            companyId = str(pressId) + "_" + str(companyName)
            print(companyId)
            if self.onlyCompany == "True":
                for k in self.company:
                    if k == companyName :
                        if (len(d['entries']) != 0):
                            result.update({companyId:d['entries']})
                            healthCheckResult.update({companyId: True})
                        else:
                            healthCheckResult.update({companyId: False})
            else:
                if (len(d['entries']) != 0):
                    result.update({companyId:d['entries']})
                    healthCheckResult.update({companyId: True})
                else:
                    healthCheckResult.update({companyId: False})
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
            print(i)
            companyList = str(i).split("_")
            print(companyList)
            companyId = companyList[0]
            companyName = companyList[1]
            for k in data[i]:
                file_title = k["title"]
                file_summary = k["summary"]
                file_link = k["link"]
                #published가 있으면 해당 값을 최초 작성 값, 없으면 updated를 최초 작성값으로 쓴다.
                if "published" in k:
                    file_article_write_time = k["published"]
                else:
                    file_article_write_time = k["updated"]
                file_articleId = self.makeArticleId(companyId, file_article_write_time)
                # file_article_write_time = datetime.strptime(file_article_write_time, '%Y-%m-%d %H:%M:%S')
                if "author" in k :
                    file_author = k["author"]
                else:
                    file_author = None
                hasher = hashlib.sha256()
                hasher.update(file_title.encode('utf-8'))
                titleId = hasher.hexdigest()
                values_to_insert.append((file_title,file_summary,file_link,file_article_write_time,file_author, companyName, companyId, file_articleId, titleId))

                # # print(file_article_write_time)
                # print(file_author)
        try:
            with conn.cursor() as cursor:
                print("sql start")
                sql = "INSERT INTO article (title, summary, link, article_write_time, author, companyName, companyId, articleId, titleId) VALUES " + ",".join("(%s,%s,%s,%s,%s,%s,%s,%s,%s)" for _ in values_to_insert)
                print(sql)
                flattened_values = [item for sublist in values_to_insert for item in sublist]
                # print(flattened_values)
                cursor.execute(sql, flattened_values)
                print(cursor)
            conn.commit()
            print(cursor.lastrowid)
        except Exception as except_detail:
            print("pymysql.err.ProgrammingError: «{}»".format(except_detail))
        finally:
            conn.close()
            print("good")
            return True
    def makeArticleId(self,pressId,datetime):
        datetimeParsed = parser.parse(datetime)
        year = str(datetimeParsed.year)
        if datetimeParsed.month < 10 :
            month = "0" + str(datetimeParsed.month)
        else :
            month = str(datetimeParsed.month)
        if datetimeParsed.day < 10 :
            day = "0" + str(datetimeParsed.day)
        else:
            day  = str(datetimeParsed.day)
        if datetimeParsed.hour < 10 :
            hour = "0" + str(datetimeParsed.hour)
        else:
            hour = str(datetimeParsed.hour)
        if datetimeParsed.minute < 10 :
            minute = "0" + str(datetimeParsed.minute)
        else:
            minute = str(datetimeParsed.minute)
        if datetimeParsed.second < 10 :
            second = "0" + str(datetimeParsed.second)
        else :
            second = str(datetimeParsed.second)

        newId  = "art_"+str(pressId)+"_"+ year+ month + day + hour + minute + second
        return newId


if __name__ == "__main__":
    rssConnector = RssConnector()
    result, healthCheckResult= rssConnector.connector()
    # print(result)
    # rssConnector.dataToMysql(result)
    # rssConnector.healthChecker(healthCheckResult)
    with open('./all.json','w') as fp:
        json.dump(result, fp, ensure_ascii=False)
