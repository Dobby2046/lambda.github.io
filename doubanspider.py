import json

from playwright.sync_api import Playwright, sync_playwright, expect
import time
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import pandas as pd
import json
# 一般在项目中使用绝对路径或与当前脚本相对路径
with open('info.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)
# 现在可以将 JSON 中的字段赋值给变量
groupname = config_data['groupname']
pagenum = int(config_data['pagenum'])
groupnum = config_data['groupnum']

client = MongoClient()
collection = client["douban"][groupname]
def parsernum(html):
    soup = BeautifulSoup(html, 'html.parser')
    element = soup.find(class_='olt')
    matches = re.findall('href="(.*?)" title="', str(element))
    print(matches)
    num=json.dumps(pd.Series(matches).to_dict())
    collection.insert_one(json.loads(num))
def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    js = """
    Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
    """
    page.add_init_script(js)
    page.goto("https:/www.douban.com/group/")
    time.sleep(20)
    for i in range(0,pagenum,25):
        print(i)
        page.goto("https://www.douban.com/group/"+groupnum+"/discussion?start="+str(i)+"&type=new")
        html = page.content()
        parsernum(html=html)
        time.sleep(5)
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
