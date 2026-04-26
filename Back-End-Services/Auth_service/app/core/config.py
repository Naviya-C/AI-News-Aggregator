import os
from dotenv import load_dotenv

load_dotenv() 

# This is direct connection to dadtabase therefore use only when you do migrations do not use day to day request handle cause it could be crash when direct connection.
# Use pooler to connect day to day connection.
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


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
