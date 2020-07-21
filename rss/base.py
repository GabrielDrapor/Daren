# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from collections import defaultdict

RSS_CACHE = defaultdict(lambda: [])


class BaseRSSHandler(object):
    def __init__(self, rss_url: str):
        rss_xml = requests.get(rss_url).content
        soup = BeautifulSoup(rss_xml, "xml")
        self.items = soup.find_all("item")
        self.title = soup.find("title").text
    

class WeiboRSSHandler(BaseRSSHandler):
    def __init__(self, rss_url: str) -> str:
        super().__init__(rss_url)
        self.latest_content = None
        latest_item = self.items[1]
        if latest_item.find("link").text in RSS_CACHE["weibo"]:
            print("No Update!")
            return
        else:
            RSS_CACHE["weibo"] = [latest_item.find("link").text]
            md = self.cvt_desc()
            self.latest_content = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*<https://weibo.com/u/{0}|@{1}>:*".format(rss_url.split("/")[-1], self.title.replace("的微博", ""))
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": md
                    }
                }
            ]
             

    def cvt_desc(self):
        desc = self.items[1].find("description").text
        if re.search("<blockquote>.*</blockquote>", desc):
            bq_raw = re.search("<blockquote>.*</blockquote>", desc).group()
            desc = re.sub("<blockquote>.*?</blockquote>", "", desc).replace("<br>", "")
            bq = re.sub("</?blockquote>", "", bq_raw).split("<br>")
            bq[0] = bq[0].replace(" - 转发 ", "")
            bq[0] = re.sub(r"<a href=\"(https.*)\" target=\"_blank\">(.*?)</a>:", "<\g<1> | \g<2>>: \n>", bq[0])
            quote_md = "\n> "+"\n> ".join(bq)
            desc += quote_md
        
        else:
            desc = desc.replace("<br>", "")
        desc += "\n\n<{}|原微博>".format(self.items[1].find("link").text)
        print(desc)
        return desc 
