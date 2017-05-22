# !/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on May 14, 2016
# @author:       Bo Zhao
# @email:        zhao2@oregonstate.edu
# @website:      http://geoviz.ceoas.oregonstate.edu
# @organization: Oregon State University


from selenium import webdriver
from settings import user, pwd

import time
import sys
from pymongo import MongoClient, errors
from bs4 import BeautifulSoup


reload(sys)
sys.setdefaultencoding('utf-8')


client = MongoClient("localhost", 27017)
db = client["facebook"]

browser = webdriver.Firefox()
browser.get("http://www.facebook.com")
browser.set_window_size(1024, 768)

username = browser.find_element_by_id("email")
password = browser.find_element_by_id("pass")
submit = browser.find_element_by_id("loginbutton")

username.send_keys(user)
password.send_keys(pwd)

submit.click()

time.sleep(8)

url = "http://www.facebook.com/search/posts/?q=standingrock%2Cnd%20change%20location"
url = "https://www.facebook.com/search/str/change+location/keywords_top?filters_rp_location=352987914761281"
url = "https://www.facebook.com/search/str/EVERYONE++check-in+at+Standing+Rock%2C+ND/keywords_blended_posts"
# url = "https://www.facebook.com/search/str/calling++check-in+at+Standing+Rock%2C+ND/keywords_blended_posts"

browser.get(url)


while len(browser.find_elements_by_xpath('//div[contains(text(), "End of Results")]')) != 1:
    time.sleep(5)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


soup = BeautifulSoup(browser.page_source, 'html5lib')
items = soup.find_all('div', class_="_401d")

for item in items:
    headshot, user_name, user_url, post_url, place, place2, place_url, place2_url, time, time2, type, like = "", "", "", "", "", "", "", "", "", "", "", 0
    try:
        headshot = item.find("div", class_="_38vo").find("img").attrs["src"]
        user_url = item.find("a", class_="profileLink").attrs["href"].replace("?hc_ref=SEARCH", "")
        user_name = item.find("a", class_="profileLink").text
        post_url = item.find("a", class_="_5pcq").attrs["href"]

        # place is in the title, place2 is in the subtitle.
        if item.find("i", class_= "_51mq") is None:
            type = "repost"
            place, place_url, place2, place2_url = "", "", "", ""
        else:
            type = "location"
            try:
                place = item.find_all("a", class_="profileLink")[1].text
                place_url = item.find_all("a", class_="profileLink")[1].attrs["href"]
            except:
                place, place_url = "", ""
            try:
                place2 = item.find_all("a", class_="_5pcq")[1].text
                place2_url = item.find_all("a", class_="_5pcq")[1].attrs["href"]
            except:
                place2, place2_url = "", ""

        time = item.find("span", class_="timestampContent").text  # u'October 31, 2016'
        time2 = item.find("abbr").attrs["title"]  # u'Monday, October 31, 2016 at 8:25am'

        content = item.find("div", class_="userContent").text
        try:
            like = int(item.find_all("span", class_="_4arz")[0].text)
        except:
            like = 0
    except:
        pass
    print headshot, user_name, place, place2, content, like

    page_json = {
        "post_url": post_url,
        "type":     type,
        "headshot": headshot,
        "user_url": user_url,
        "user_name": user_name,
        "place_url": place_url,
        "place": place,
        "place2_url": place2_url,
        "place2": place2,
        "content": content,
        "like": like,
        "time": time,
        "time2": time2
    }
    try:
        db.posts.insert_one(page_json)
    except errors.DuplicateKeyError:
        print 'This post has already been inserted.'


print len(items)
browser.close()
client.close()
print "finished"
