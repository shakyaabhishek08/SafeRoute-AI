from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import chat_collection
from app.services.chatbot_service import chatbot

router = APIRouter(
    prefix="/api",
    tags=["AI Assistant"]
)


# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# ---------------------------------------------------------
# Response Model
# ---------------------------------------------------------

class ChatResponse(BaseModel):
    success: bool
    session_id: str
    reply: str


# ---------------------------------------------------------
# Chat API
# ---------------------------------------------------------

@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    try:

        session_id = (
            request.session_id
            if request.session_id
            else str(uuid.uuid4())
        )

        user_message = request.message.strip()

        if user_message == "":

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        # ---------------------------------------
        # Ask Groq
        # ---------------------------------------

        ai_reply = chatbot.ask(
            user_message
        )

        # ---------------------------------------
        # Save Chat History
        # ---------------------------------------

        await chat_collection.insert_one(

            {

                "session_id": session_id,

                "question": user_message,

                "answer": ai_reply,

                "created_at": datetime.utcnow()

            }

        )

        return {

            "success": True,

            "session_id": session_id,

            "reply": ai_reply

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )