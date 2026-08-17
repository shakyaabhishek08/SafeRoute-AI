from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.database import users_collection
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# --------------------------------------------------
# Request Models
# --------------------------------------------------

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmergencyContactsRequest(BaseModel):
    contacts: List[str]


# --------------------------------------------------
# Helper Function
# --------------------------------------------------

async def get_current_user(authorization: Optional[str]):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )

    token = authorization.replace("Bearer ", "")

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = await users_collection.find_one(
        {
            "email": email
        }
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# --------------------------------------------------
# Signup
# --------------------------------------------------

@router.post("/signup")
async def signup(data: SignupRequest):

    existing = await users_collection.find_one(
        {
            "email": data.email
        }
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = {

        "name": data.name,

        "email": data.email,

        "password": hash_password(data.password),

        "role": "user",

        "emergency_contacts": []

    }

    result = await users_collection.insert_one(user)

    token = create_access_token({

        "id": str(result.inserted_id),

        "email": user["email"],

        "role": user["role"]

    })

    return {

        "success": True,

        "message": "Account created successfully",

        "token": token,

        "user": {

            "id": str(result.inserted_id),

            "name": user["name"],

            "email": user["email"],

            "role": user["role"],

            "emergency_contacts": []

        }

    }


# --------------------------------------------------
# Login
# --------------------------------------------------

@router.post("/login")
async def login(data: LoginRequest):

    user = await users_collection.find_one(
        {
            "email": data.email
        }
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({

        "id": str(user["_id"]),

        "email": user["email"],

        "role": user["role"]

    })

    return {

        "success": True,

        "message": "Login successful",

        "token": token,

        "user": {

            "id": str(user["_id"]),

            "name": user["name"],

            "email": user["email"],

            "role": user["role"],

            "emergency_contacts": user.get(
                "emergency_contacts",
                []
            )

        }

    }
    # --------------------------------------------------
# Current Logged-in User
# --------------------------------------------------

@router.get("/me")
async def get_me(
    authorization: Optional[str] = Header(None)
):

    user = await get_current_user(
        authorization
    )

    return {

        "success": True,

        "user": {

            "id": str(user["_id"]),

            "name": user["name"],

            "email": user["email"],

            "role": user["role"],

            "emergency_contacts": user.get(
                "emergency_contacts",
                []
            )

        }

    }


# --------------------------------------------------
# Logout
# --------------------------------------------------

@router.post("/logout")
async def logout():

    return {

        "success": True,

        "message": "Logout successful"

    }


# --------------------------------------------------
# Get Emergency Contacts
# --------------------------------------------------

@router.get("/emergency-contacts")
async def get_emergency_contacts(
    authorization: Optional[str] = Header(None)
):

    user = await get_current_user(
        authorization
    )

    return {

        "success": True,

        "contacts": user.get(
            "emergency_contacts",
            []
        )

    }


# --------------------------------------------------
# Update Emergency Contacts
# --------------------------------------------------

@router.put("/emergency-contacts")
async def update_emergency_contacts(
    data: EmergencyContactsRequest,
    authorization: Optional[str] = Header(None)
):

    user = await get_current_user(
        authorization
    )

    await users_collection.update_one(

        {
            "_id": user["_id"]
        },

        {
            "$set": {

                "emergency_contacts": data.contacts

            }

        }

    )

    updated_user = await users_collection.find_one(

        {

            "_id": user["_id"]

        }

    )

    return {

        "success": True,

        "message": "Emergency contacts updated successfully",

        "contacts": updated_user.get(

            "emergency_contacts",

            []

        )

    }


# --------------------------------------------------
# Delete Emergency Contact
# --------------------------------------------------

@router.delete("/emergency-contacts")
async def delete_emergency_contact(
    contact: str,
    authorization: Optional[str] = Header(None)
):

    user = await get_current_user(
        authorization
    )

    contacts = user.get(
        "emergency_contacts",
        []
    )

    if contact not in contacts:

        raise HTTPException(

            status_code=404,

            detail="Contact not found"

        )

    contacts.remove(contact)

    await users_collection.update_one(

        {

            "_id": user["_id"]

        },

        {

            "$set": {

                "emergency_contacts": contacts

            }

        }

    )

    return {

        "success": True,

        "message": "Emergency contact removed",

        "contacts": contacts

    }