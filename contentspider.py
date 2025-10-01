from playwright.sync_api import Playwright, sync_playwright, expect
import time
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import pandas as pd
from parsel import Selector
import json
# 一般在项目中使用绝对路径或与当前脚本相对路径
with open('info.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)
# 现在可以将 JSON 中的字段赋值给变量
groupname = config_data['groupname']
pagenum = int(config_data['pagenum'])
groupnum = config_data['groupnum']
client = MongoClient()
collection = client["douban"][(groupname+"文本")]
collection1 = client["douban"][(groupname+"url")]
num = pd.DataFrame(list(collection1.find()))
dfnum=num.sort_values(by='index')
start_row = 1

def parsernum(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find(class_='article')
        selector = Selector(text=str(element))
        element2 = element.find(class_="topic-reply")
        selector2 = Selector(text=str(element2))
        article = re.findall('<h1>(.*?)<div class="event-labels">', str(element), re.DOTALL)[0]
        location = selector.css('.ip-location').re('"ip-location">(.*?)</span>')[0]
        createtime = selector.css('.topic-meta .create-time').re('>(.*?)</span>')[0]
        topicrichtext = '/n'.join(selector.css('.rich-content.topic-richtext').re('>(.*?)</p>'))
        pubtime = selector2.css('.pubtime').re('>(.*?)</span>')
        # allrefcontent=selector2.css('.reply-quote-content').re('>(.*?)</span>')[1]
        replycontent = selector.css('.reply-content').re('>(.*?)</p>')
        # collection.insert_one({"title":matchestitle,"content":"".join(matchescontent),"time":matchestime[0][1],"reple":matchesreply})
        result = {"article": article, "location": location, "topicrichtext": topicrichtext, "createtime": createtime,
                  "pubtime": pubtime, "replycontent": replycontent}
        collection.insert_one(result)
    except Exception as msg:  # 捕获所有异常
        print("内部异常:%s" % msg)
    return 0


def should_block_request(request):
    if request.resource_type == "image":
        return True
    return False

def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    js = """
    Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
    """
    page.add_init_script(js)
    #page.route("**/*.{png,jpg,jpeg}", should_block_request)
    page.goto("https:/www.douban.com/group/")
    time.sleep(20)
    for index, row in dfnum.iloc[start_row:].iterrows():
        print(row['num'])
        try:
            print(row['index'])
            page.goto(row['num'])
            html = page.content()
            parsernum(html=html)
            time.sleep(5)
        except Exception as msg:  # 捕获所有异常
            print("外部异常:%s" % msg)
        continue
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
