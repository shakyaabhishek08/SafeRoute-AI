from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import incidents_collection
from datetime import datetime
from bson import ObjectId
import random

router = APIRouter(
    prefix="/api",
    tags=["Incidents"]
)


# ----------------------------------------
# Request Model
# ----------------------------------------

class IncidentRequest(BaseModel):
    type: str
    severity: str
    description: str
    lat: float
    lng: float
    location_name: str = "Unknown"
    reporter_name: str = "Anonymous"


# ----------------------------------------
# Report Incident
# ----------------------------------------

@router.post("/report")
async def create_report(data: IncidentRequest):

    incident = {

        "type": data.type,

        "severity": data.severity,

        "description": data.description,

        "location": {

            "lat": data.lat,

            "lng": data.lng

        },

        "location_name": data.location_name,

        "reporter_name": data.reporter_name,

        "status": "active",

        "verified": False,

        "upvotes": 0,

        "downvotes": 0,

        "created_at": datetime.utcnow()

    }

    result = await incidents_collection.insert_one(
        incident
    )

    incident["_id"] = str(result.inserted_id)

    return {

        "success": True,

        "message": "Incident reported successfully",

        "incident": incident

    }


# ----------------------------------------
# Get All Incidents
# ----------------------------------------

@router.get("/incidents")
async def get_incidents():

    incidents = []

    cursor = incidents_collection.find().sort(
        "created_at",
        -1
    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        incidents.append(item)

    return incidents


# ----------------------------------------
# Seed Demo Incidents
# ----------------------------------------

@router.get("/seed-incidents")
async def seed():

    count = await incidents_collection.count_documents({})

    if count > 0:

        return {

            "message": "Already Seeded"

        }

    demo = []

    for _ in range(25):

        demo.append({

            "type": random.choice([

                "crime",

                "harassment",

                "accident",

                "poor_lighting",

                "other"

            ]),

            "severity": random.choice([

                "low",

                "medium",

                "high"

            ]),

            "description": "Demo Incident",

            "location": {

                "lat": 12.9716 + random.uniform(-0.03,0.03),

                "lng": 77.5946 + random.uniform(-0.03,0.03)

            },

            "location_name": "Bangalore",

            "reporter_name": "Demo User",

            "status": "active",

            "verified": False,

            "upvotes": random.randint(0,20),

            "downvotes": random.randint(0,5),

            "created_at": datetime.utcnow()

        })

    await incidents_collection.insert_many(demo)

    return {

        "message": "25 Demo Incidents Added"

    }


# ----------------------------------------
# Delete Incident
# ----------------------------------------

@router.delete("/incidents/{id}")
async def delete_incident(id: str):

    try:

        result = await incidents_collection.delete_one(

            {

                "_id": ObjectId(id)

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

            detail="Incident Not Found"

        )

    return {

        "message": "Incident Deleted Successfully"

    }


# ----------------------------------------
# My Reports
# ----------------------------------------

@router.get("/reports/mine")
async def my_reports():

    reports = []

    cursor = incidents_collection.find().sort(

        "created_at",

        -1

    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        reports.append(item)

    return reports