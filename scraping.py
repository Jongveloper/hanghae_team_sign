from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.sign

driver = webdriver.Chrome('./chromedriver')

url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=primera&tab=team"

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


