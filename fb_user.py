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

# posts = db.posts.find({"orig_loc": {"$exists": False}})
posts = db.posts.find({"orig_loc": ""})


count = posts.count()
living_place_keyword = '/about?section=living'
recent_place_keyword = '/places_recent'


# login
# browser = webdriver.Firefox(executable_path='/Users/bo/Workspace/geckodriver')
# browser = webdriver.Firefox(executable_path='C:/Workspace/geockodriver.exe')
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

print count

items = []

for post in posts:
    items.append(post['user_url'])

for item in items:
    user_url = item
    orig_loc = ""
    living_place_url = user_url + living_place_keyword
    time.sleep(3)
    print living_place_url
    browser.get(living_place_url)
    soup = BeautifulSoup(browser.page_source, 'html5lib')
    orig_loc_items = soup.findAll("span", class_="_50f5 _50f7")

    if len(orig_loc_items) != 0:
        # the location in the living place
        orig_loc = orig_loc_items[0].text
        # how to geocode lat, lng.
        lat, lng = 0, 0
    else:
        # the location in the recent visited places
        recent_place_url = user_url + recent_place_keyword
        browser.get(recent_place_url)
        soup = BeautifulSoup(browser.page_source, 'html5lib')
        checkin_items = soup.findAll("a", class_="_gx7")
        lat = 0
        lng = 0
        orig_loc = ""
        if len(checkin_items) != 0:
            checkin_url = checkin_items[0].attrs["href"]
            orig_loc = checkin_items[0].attrs["title"]
            time.sleep(3)
            browser.get(checkin_url)
            soup = BeautifulSoup(browser.page_source, 'html5lib')
            try:
                checkin_map_url = soup.find("img", class_="_a3f").attrs["src"]
                # print checkin_map_url
                # https://external.fsnc1-1.fna.fbcdn.net/static_map.php?v=29&osm_provider=2&size=306x98&zoom=15&markers=34.10045944%2C-118.32971409&language=en_US
                if ".png%7C" in checkin_map_url:
                    latlng = checkin_map_url.split(".png%7C")[1].split("&language")[0].split("%2C")
                else:
                    latlng = checkin_map_url.split("markers=")[1].split("&language")[0].split("%2C")

                lat = float(latlng[0])
                lng = float(latlng[1])
                try:
                    orig_loc = soup.find(id="u_0_2t").find("a").text
                except:
                    pass
            except:
                pass

    print orig_loc, lat, lng

    page_json = {
        "lat": lat,
        "lng": lng,
        "orig_loc": orig_loc
    }

    db.posts.update({'user_url': user_url}, {'$set': page_json})


browser.close()
client.close()
print "finished"
