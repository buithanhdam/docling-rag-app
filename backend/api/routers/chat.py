from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.mysql import get_db
from api.services.chat import ChatService
from api.schemas.chat import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse
)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(conv_create: ConversationCreate, db: Session = Depends(get_db)):
    return await ChatService.create_conversation(db, conv_create)

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    return await ChatService.get_conversation(db, conversation_id)

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_all_conversations(skip: int = 0, limit: int = 100, agent_id: Optional[int] = None, db: Session = Depends(get_db)):
    return await ChatService.get_all_conversations(db, skip, limit, agent_id)

@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: int, conv_update: ConversationUpdate, db: Session = Depends(get_db)):
    return await ChatService.update_conversation(db, conversation_id, conv_update)

@router.delete("/conversations/{conversation_id}", response_model=bool)
async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    return await ChatService.delete_conversation(db, conversation_id)

@router.post("/messages", response_model=MessageResponse)
async def add_message(message: MessageCreate, db: Session = Depends(get_db)):
    return await ChatService.add_message(db, message)