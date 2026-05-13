# -*- coding: UTF-8 -*-
# Centralized API configuration for all ReactionSeek scripts.
from openai import OpenAI

BASE_URL = "https://api.openai.com/v1"
API_KEY = ""
MODEL = "gpt-3.5-turbo-16k"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
