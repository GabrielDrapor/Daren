# -*- coding: utf-8 -*-

import os
from slack import WebClient

Daren = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
