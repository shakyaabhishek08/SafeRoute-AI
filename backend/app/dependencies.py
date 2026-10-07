
from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import decode_access_token
from app.database import users_collection


# -------------------------------------------------------
# HTTP BEARER SECURITY
# -------------------------------------------------------

security = HTTPBearer()


# -------------------------------------------------------
# Get Current Logged-in User
# -------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):
    """
    Validate JWT and return the logged-in user.
    """

    # ---------------------------------------------------
    # Get token from Authorization header
    # ---------------------------------------------------

    token = credentials.credentials

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing"
        )

    # ---------------------------------------------------
    # Decode JWT
    # ---------------------------------------------------

    payload = decode_access_token(
        token
    )

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # ---------------------------------------------------
    # Get email from token
    # ---------------------------------------------------

    email = payload.get(
        "email"
    )

    if not email:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # ---------------------------------------------------
    # Find user in MongoDB
    # ---------------------------------------------------

    user = await users_collection.find_one(
        {
            "email": email
        }
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # ---------------------------------------------------
    # Never return password
    # ---------------------------------------------------

    user.pop(
        "password",
        None
    )

    return user


# -------------------------------------------------------
# Get Current Admin User
# -------------------------------------------------------

async def get_admin_user(
    current_user=Depends(
        get_current_user
    )
):
    """
    Allow access only to admin users.
    """

    if current_user.get(
        "role"
    ) != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )

    return current_user