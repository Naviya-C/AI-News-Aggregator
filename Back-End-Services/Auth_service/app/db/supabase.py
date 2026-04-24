from sqlalchemy import create_engine

from app.core.config import DATABASE_URL

# Direct connect with supabase checking
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")