from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "gizli-anahtar-bunu-degistir"
ALGORITHM = "HS256"
TOKEN_SURE = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sifre_hashle(sifre: str):
    return pwd_context.hash(sifre)

def sifre_dogrula(sifre: str, hash: str):
    return pwd_context.verify(sifre, hash)

def token_olustur(data: dict):
    kopya = data.copy()
    sure = datetime.utcnow() + timedelta(minutes=TOKEN_SURE)
    kopya.update({"exp": sure})
    return jwt.encode(kopya, SECRET_KEY, algorithm=ALGORITHM)

def token_coz(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
