from sqlalchemy import create_engine
from app.core.config import DATABASE_URL, DATABASE_URL_P
from sqlalchemy.pool import NullPool

engine = create_engine(DATABASE_URL)

# Test the connection for direct connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")
    
    
    
engine = create_engine(DATABASE_URL_P, poolclass = NullPool)
# Test pooler connection 
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")