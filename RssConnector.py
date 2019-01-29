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
        with open('config.json') as json_data_file:
            data0 = json.load(json_data_file)
        self.jsonConfig = data0['urlFile']
        self.healthConfig = data0['healthFile']
        self.result = 0
        #Initialization 정의

    def connector(self):
        result = {}
        healthCheckResult = {}
        with open(self.jsonConfig,"rt", encoding= "utf-8") as f:
            data = json.load(f)
        for i in range(len(data["items"])):
            url = data["items"][i]['rss_url']["all"]
            d = feedparser.parse(url)
            if (len(d['entries']) != 0):
                result.update({data['items'][i]['company']:d['entries']})
                healthCheckResult.update({data['items'][i]['company']: True})
                # print(data["items"][i]['company'])
                # print(d['feed']['title'])
                # print(d['feed']['title'])
                # print(d['entries'][0])
            else:
                healthCheckResult.update({data['items'][i]['company']: False})
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


if __name__ == "__main__":
    rssConnector = RssConnector()
    result, healthCheckResult= rssConnector.connector()
    rssConnector.healthChecker(healthCheckResult)
    print("done")
