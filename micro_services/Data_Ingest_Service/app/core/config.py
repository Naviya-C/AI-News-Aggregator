import os
from dotenv import load_dotenv

load_dotenv() 

DATABASE_URL = os.getenv('CONN_STRING')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = os.getenv('NEWS_API_URL')

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")