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
        latest_item = self.items[0]
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
        desc = self.items[0].find("description").text
        if re.search("<blockquote>.*</blockquote>", desc):
            bq_raw = re.search("<blockquote>.*</blockquote>", desc).group()
            desc = re.sub("<blockquote>.*?</blockquote>", "", desc).replace("<br>", "")
            bq = re.sub("</?blockquote>", "", bq_raw).split("<br>")
            bq[0] = bq[0].replace(" - 转发 ", "")
            repost_user_line = re.sub(r"<a href=\"(https.*)\" target=\"_blank\">(.*?)</a>:", "<\g<1> | \g<2>>: ", bq[0])
            repost_content_list = []
            bq[0] = re.sub(r"<a href=\"(https.*)\" target=\"_blank\">(.*?)</a>:", "", bq[0])
            for row in bq:
                repost_line = ""
                row_elems = BeautifulSoup(html.unescape(row), "html").find("p").children
                for elem in row_elems:
                    if elem.name is None: #plain text
                        repost_line += elem.title()
                    else:
                        if elem.name == "a":
                             if "data-url" in elem.attrs:
                                 repost_line += "<{0}|{1}>".format(elem.attrs["data-url"], elem.text)
                             elif "href" in elem.attrs:
                                 repost_line += "<{0}|{1}>".format(elem.attrs["href"], elem.text)
                repost_content_list.append(repost_line)
            repost_content_list.insert(0, repost_user_line)
            
            desc = "\n> "+"\n> ".join(repost_content_list)
        
        else:
            desc = desc.replace("<br>", "")
        desc += "\n\n<{}|原微博>".format(self.items[0].find("link").text)
        print(desc)
        return desc 
