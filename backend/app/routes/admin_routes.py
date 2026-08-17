from fastapi import APIRouter, HTTPException, Depends, Header
from bson import ObjectId
from app.auth import decode_access_token

from app.database import (
    users_collection,
    incidents_collection,
    journeys_collection
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)
# ---------------------------------------------------------
# Get Current Admin
# ---------------------------------------------------------

async def get_admin_user(
    authorization: str = Header(None)
):

    if authorization is None:

        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    payload = decode_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = await users_collection.find_one(
        {
            "email": payload["email"]
        }
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access only"
        )

    return user

# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@router.get("/dashboard")
async def dashboard(
    admin=Depends(get_admin_user)
):

    total_users = await users_collection.count_documents({})

    total_incidents = await incidents_collection.count_documents({})

    total_journeys = await journeys_collection.count_documents({})

    recent_users = []

    cursor = users_collection.find().sort(
        "_id",
        -1
    ).limit(5)

    async for user in cursor:

        user["_id"] = str(user["_id"])

        user.pop("password", None)

        recent_users.append(user)

    recent_incidents = []

    cursor = incidents_collection.find().sort(
        "created_at",
        -1
    ).limit(5)

    async for item in cursor:

        item["_id"] = str(item["_id"])

        recent_incidents.append(item)

    recent_journeys = []

    cursor = journeys_collection.find().sort(
        "created_at",
        -1
    ).limit(5)

    async for item in cursor:

        item["_id"] = str(item["_id"])

        recent_journeys.append(item)

    return {

        "success": True,

        "statistics": {

            "users": total_users,

            "incidents": total_incidents,

            "journeys": total_journeys

        },

        "recent_users": recent_users,

        "recent_incidents": recent_incidents,

        "recent_journeys": recent_journeys

    }


# ---------------------------------------------------------
# Get Users
# ---------------------------------------------------------

@router.get("/users")
async def get_users(
    admin=Depends(get_admin_user)
):

    users = []

    cursor = users_collection.find().sort(
        "name",
        1
    )

    async for user in cursor:

        user["_id"] = str(user["_id"])

        user.pop("password", None)

        users.append(user)

    return {

        "success": True,

        "users": users,

        "count": len(users)

    }


# ---------------------------------------------------------
# Delete User
# ---------------------------------------------------------

@router.delete("/users/{user_id}")
async def delete_user(user_id: str,admin=Depends(get_admin_user)):

    try:

        result = await users_collection.delete_one(

            {

                "_id": ObjectId(user_id)

            }

        )

    except:

        raise HTTPException(

            status_code=400,

            detail="Invalid User ID"

        )

    if result.deleted_count == 0:

        raise HTTPException(

            status_code=404,

            detail="User not found"

        )

    return {

        "success": True,

        "message": "User deleted successfully"

    }


# ---------------------------------------------------------
# Get Incidents
# ---------------------------------------------------------

@router.get("/incidents")
async def get_incidents(
    admin=Depends(get_admin_user)
):

    incidents = []

    cursor = incidents_collection.find().sort(
        "created_at",
        -1
    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        incidents.append(item)

    return {

        "success": True,

        "incidents": incidents,

        "count": len(incidents)

    }


# ---------------------------------------------------------
# Delete Incident
# ---------------------------------------------------------

@router.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: str):

    try:

        result = await incidents_collection.delete_one(

            {

                "_id": ObjectId(incident_id)

            }

        )

    except:

        raise HTTPException(

            status_code=400,

            detail="Invalid Incident ID"

        )

    if result.deleted_count == 0:

        raise HTTPException(

            status_code=404,

            detail="Incident not found"

        )

    return {

        "success": True,

        "message": "Incident deleted successfully"

    }


# ---------------------------------------------------------
# Get Journeys
# ---------------------------------------------------------

@router.get("/journeys")
async def get_journeys(
    admin=Depends(get_admin_user)
):

    journeys = []

    cursor = journeys_collection.find().sort(
        "created_at",
        -1
    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        journeys.append(item)

    return {

        "success": True,

        "journeys": journeys,

        "count": len(journeys)

    }


# ---------------------------------------------------------
# Delete Journey
# ---------------------------------------------------------

@router.delete("/journeys/{journey_id}")
async def delete_journey(journey_id: str):

    try:

        result = await journeys_collection.delete_one(

            {

                "_id": ObjectId(journey_id)

            }

        )

    except:

        raise HTTPException(

            status_code=400,

            detail="Invalid Journey ID"

        )

    if result.deleted_count == 0:

        raise HTTPException(

            status_code=404,

            detail="Journey not found"

        )

    return {

        "success": True,

        "message": "Journey deleted successfully"

    }