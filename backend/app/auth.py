from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# ---------------------------------------
# Load Environment Variables
# ---------------------------------------

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")

if not SECRET_KEY:
    raise ValueError("JWT_SECRET not found in .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ---------------------------------------
# Password Hashing
# ---------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hash plain password before storing in database.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify entered password with stored hash.
    """
    return pwd_context.verify(
        password,
        hashed_password
    )


# ---------------------------------------
# JWT Token
# ---------------------------------------

def create_access_token(data: dict) -> str:
    """
    Create JWT access token.
    """

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=ACCESS_TOKEN_EXPIRE_DAYS
    )

    payload.update({
        "exp": expire
    })

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decode_access_token(token: str):
    """
    Decode JWT token.
    Returns payload if valid otherwise None.
    """

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None


# ---------------------------------------
# Helper Function
# ---------------------------------------

def get_user_email(token: str):
    """
    Extract email from JWT token.
    """

    payload = decode_access_token(token)

    if payload is None:
        return None

    return payload.get("email")