from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display
from time import sleep
from pymongo import MongoClient

<<<<<<< HEAD
client = MongoClient('mongodb://test:test@localhost', 27017)
=======


client = MongoClient('localhost', 27017)
>>>>>>> 8adfaed0f1fc394697210a9656716029e790a529
db = client.sign

display = Display(visible=0, size=(1920,1080))
display.start()

<<<<<<< HEAD
path = '/home/ubuntu/chromedriver'
driver = webdriver.Chrome(path)

url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=seria&tab=team"
=======

#영국
# # url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=epl&tab=team"

#독일
# url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=bundesliga&tab=team"

#이탈리아
url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=seria&tab=team"

#프랑스
# # url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=ligue1&tab=team"
>>>>>>> 8adfaed0f1fc394697210a9656716029e790a529

driver.get(url)
sleep(1)

req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')
team_name = soup.select("#content > div.record_tab > ul > li.selected > a > span > span.title")[0].text
team_rank_list = soup.select("#wfootballTeamRecordBody > table > tbody > tr")

for team in team_rank_list:
    num = team.select('.num > div.inner > strong')[0].text

    name = team.select('.name')[0].text
    print(num, name)

    if bool(db.teams.find_one({'t_name': name})):
        doc = {
            '순위': num,
            't_name': name

        }

    else:
        doc = {
            'lank': num,
            't_name': name,
            'league': team_name
        }
        db.teams.insert_one(doc)


name = team.select('.name')[0].text
print(num, name)

