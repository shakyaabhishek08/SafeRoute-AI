from fastapi import APIRouter, HTTPException
from app.database import chat_collection

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat History"]
)


# --------------------------------------------------
# Get Complete Chat History
# --------------------------------------------------

@router.get("/history")
async def get_chat_history():

    chats = []

    cursor = chat_collection.find().sort(
        "created_at",
        -1
    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        chats.append(item)

    return {

        "success": True,

        "count": len(chats),

        "history": chats

    }


# --------------------------------------------------
# Get Chat History by Session
# --------------------------------------------------

@router.get("/history/{session_id}")
async def get_session_history(session_id: str):

    chats = []

    cursor = chat_collection.find(
        {
            "session_id": session_id
        }
    ).sort(
        "created_at",
        1
    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        chats.append(item)

    return {

        "success": True,

        "session_id": session_id,

        "count": len(chats),

        "history": chats

    }


# --------------------------------------------------
# Delete One Chat Session
# --------------------------------------------------

@router.delete("/history/{session_id}")
async def delete_session(session_id: str):

    result = await chat_collection.delete_many(
        {
            "session_id": session_id
        }
    )

    if result.deleted_count == 0:

        raise HTTPException(

            status_code=404,

            detail="Session not found"

        )

    return {

        "success": True,

        "message": "Chat session deleted",

        "deleted": result.deleted_count

    }


# --------------------------------------------------
# Delete Complete Chat History
# --------------------------------------------------

@router.delete("/history")
async def clear_chat_history():

    result = await chat_collection.delete_many({})

    return {

        "success": True,

        "message": "All chat history deleted",

        "deleted": result.deleted_count

    }