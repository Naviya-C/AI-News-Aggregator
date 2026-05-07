from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import SECRET_KEY, ALGORITHM

def validation(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        
        return payload
    
    except ExpiredSignatureError:
        return "Token has expired"
    except JWTError:
        return "Invalid token (Tampered with or wrong key)"
        