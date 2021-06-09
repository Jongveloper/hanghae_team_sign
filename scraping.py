from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

driver = webdriver.Chrome('./chromedriver')


url = "https://sports.news.naver.com/wfootball/record/index.nhn?category=epl&tab=team"

driver.get(url)
sleep(1)

req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')

team_rank_list = soup.select("#wfootballTeamRecordBody > table > tbody > tr")

for team in team_rank_list:
 num = team.select('.num > div.inner > strong')[0].text

 name = team.select('.name')[0].text
 print(num, name)