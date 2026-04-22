from passlib.context import CryptContext
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # used to manage hashing algo and handle hashing+verification. Schema can changed.

def hash_password(password: str):
    """
    In here, why we not just hash password only using 'bcrypt', cause beccrypt only can do <72byte long passwords encrypts but what if it exeeds. Get truncated or error.
    Therefore:
        - We use layered hashing, not double hash.
        - sha256 converts any lenght of password to fixed length 64hex chars.
        - The input to bcrypt to hash.
    Why not only use either of them:
        - Only SHA256 gives easy attacks.
        - Only becrypt give length issue.
    """
    hashed = hashlib.sha256(password.encode()).hexdigest() # same input give u same output everytime.
    return pwd_context.hash(hashed) # same output different hashes. Cause bcrypt adds RANDOM SALT.

def verify_password(plain_password, hashed_password):
    hashed = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(hashed, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy() # prevent the original data modifications
    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
