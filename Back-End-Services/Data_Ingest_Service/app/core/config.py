import os
from dotenv import load_dotenv

load_dotenv() 

# This is Direct database access, used to migrations
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"


# This is pooler connection to dadtabase. Use this for normal user interactions.
USER_P = os.getenv("user_P")
PASSWORD_P = os.getenv("password_P")
HOST_P = os.getenv("host_P")
PORT_P = os.getenv("port_P")
DBNAME_P = os.getenv("dbname_P")

DATABASE_URL_P = f"postgresql+psycopg2://{USER_P}:{PASSWORD_P}@{HOST_P}:{PORT_P}/{DBNAME_P}?sslmode=require"

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = os.getenv('NEWS_API_URL')

# Qdrant database access details
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")