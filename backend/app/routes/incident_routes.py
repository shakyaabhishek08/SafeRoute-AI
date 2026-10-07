from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.database import incidents_collection
from app.dependencies import get_current_user, get_admin_user


router = APIRouter(
    prefix="/api",
    tags=["Incidents"]
)


# =======================================================
# REQUEST MODEL
# =======================================================

class IncidentRequest(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., min_length=1, max_length=20)
    description: str = Field(..., min_length=1, max_length=1000)

    lat: float
    lng: float

    location_name: str = Field(
        default="Unknown",
        max_length=200
    )


# =======================================================
# CREATE INCIDENT REPORT
# =======================================================

@router.post("/report")
async def create_report(
    data: IncidentRequest,
    current_user=Depends(get_current_user)
):
    """
    Create a new incident report.

    The incident is automatically linked to the
    authenticated user.
    """

    user_id = str(
        current_user["_id"]
    )

    user_name = current_user.get(
        "name",
        "Anonymous"
    )

    incident = {
        "user_id": user_id,

        "type": data.type.strip(),

        "severity": data.severity.strip().lower(),

        "description": data.description.strip(),

        "location": {
            "lat": data.lat,
            "lng": data.lng
        },

        "location_name": data.location_name.strip(),

        "reporter_name": user_name,

        "status": "active",

        "verified": False,

        "upvotes": 0,

        "downvotes": 0,

        "created_at": datetime.utcnow()
    }

    result = await incidents_collection.insert_one(
        incident
    )

    incident["_id"] = str(
        result.inserted_id
    )

    return {
        "success": True,
        "message": "Incident reported successfully",
        "incident": incident
    }


# =======================================================
# GET ALL ACTIVE INCIDENTS
# =======================================================

@router.get("/incidents")
async def get_incidents():
    """
    Return active incidents.

    This endpoint is intentionally public because
    the route/map system needs incident information
    to evaluate routes.
    """

    incidents = []

    cursor = incidents_collection.find(
        {
            "status": "active"
        }
    ).sort(
        "created_at",
        -1
    )

    async for item in cursor:

        item["_id"] = str(
            item["_id"]
        )

        incidents.append(item)

    return {
        "success": True,
        "incidents": incidents,
        "count": len(incidents)
    }


# =======================================================
# SEED DEMO INCIDENTS
# =======================================================

@router.get("/seed-incidents")
async def seed_incidents(
    current_user=Depends(get_admin_user)
):
    """
    Create demo incidents for development/testing.

    Admin access only.
    """

    import random

    count = await incidents_collection.count_documents({})

    if count > 0:

        return {
            "success": True,
            "message": "Incidents already exist. Demo data was not added."
        }

    demo = []

    for _ in range(25):

        demo.append(
            {
                "user_id": "demo",

                "type": random.choice(
                    [
                        "crime",
                        "harassment",
                        "accident",
                        "poor_lighting",
                        "other"
                    ]
                ),

                "severity": random.choice(
                    [
                        "low",
                        "medium",
                        "high"
                    ]
                ),

                "description": "Demo Incident",

                "location": {
                    "lat": 12.9716 + random.uniform(
                        -0.03,
                        0.03
                    ),

                    "lng": 77.5946 + random.uniform(
                        -0.03,
                        0.03
                    )
                },

                "location_name": "Bangalore",

                "reporter_name": "Demo User",

                "status": "active",

                "verified": False,

                "upvotes": random.randint(
                    0,
                    20
                ),

                "downvotes": random.randint(
                    0,
                    5
                ),

                "created_at": datetime.utcnow()
            }
        )

    await incidents_collection.insert_many(
        demo
    )

    return {
        "success": True,
        "message": "25 demo incidents added"
    }


# =======================================================
# MY REPORTS
# =======================================================

@router.get("/reports/mine")
async def my_reports(
    current_user=Depends(get_current_user)
):
    """
    Return only incidents reported by
    the authenticated user.
    """

    user_id = str(
        current_user["_id"]
    )

    reports = []

    cursor = incidents_collection.find(
        {
            "user_id": user_id
        }
    ).sort(
        "created_at",
        -1
    )

    async for item in cursor:

        item["_id"] = str(
            item["_id"]
        )

        reports.append(item)

    return {
        "success": True,
        "reports": reports,
        "count": len(reports)
    }


# =======================================================
# DELETE INCIDENT — ADMIN ONLY
# =======================================================

@router.delete("/incidents/{incident_id}")
async def delete_incident(
    incident_id: str,
    admin=Depends(get_admin_user)
):
    """
    Delete an incident.

    Only administrators are allowed to perform
    this operation.
    """

    try:

        object_id = ObjectId(
            incident_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid Incident ID"
        )

    result = await incidents_collection.delete_one(
        {
            "_id": object_id
        }
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