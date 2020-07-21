# -*- coding: utf-8 -*-
from rss.base import WeiboRSSHandler
from client import Daren

wb_hndlr = WeiboRSSHandler("https://rsshub.app/weibo/user/5992829552")
Daren.chat_postMessage(channel="#weibo_update", blocks=wb_hndlr.latest_content)
