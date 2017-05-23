# !/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on May 14, 2016
# @author:       Bo Zhao
# @email:        zhao2@oregonstate.edu
# @website:      http://geoviz.ceoas.oregonstate.edu
# @organization: Oregon State University


import time
import sys
from pymongo import MongoClient

import geocoder


reload(sys)
sys.setdefaultencoding('utf-8')

client = MongoClient("localhost", 27017)
db = client["facebook"]

# posts = db.posts.find({"orig_loc": {"$exists": False}})
posts = db.posts.find({"orig_loc": {"$ne": ""}})

print posts.count()


locs = []

for post in posts:
    try:
        if post['lat'] == -1 and post['orig_loc'] != "":
            locs.append(post['orig_loc'])
    except:
        pass


print len(locs)

output = []
for loc in locs:
    if loc not in output:
        output.append(loc)

print len(output)

for loc in output:

        g = geocoder.google(loc)
        try:
            lat = g.latlng[0]
            lng = g.latlng[1]
        except:
            lat = -1
            lng = -1

        page_json = {
            "lat": lat,
            "lng": lng,
        }

        print loc, lat, lng

        db.posts.update_many({'orig_loc': loc}, {'$set': page_json})


client.close()
print "finished"
