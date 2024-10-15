from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.agents.code_generator import CodeGenerator
from app.models.chat import ChatContextType
from app.models.message import MessageType
from app.models.user_file import UserFile
from .auth_router import router as auth_router
from .models import User, Message, Chat
from .config import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
import os

app = FastAPI()

app.add_middleware(SessionMiddleware, 
                   secret_key="add any string...",
                   https_only=False)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)


templates = Jinja2Templates(directory="templates")
@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )

@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )

@app.get("/api/session")
def get_session(request: Request):
    user = request.session.get('user')
    if user:
        return {"user": user}
    return {"user": None}

@app.get("/api/users/{userId}/chats/{chatContext}/messages")
def get_user_messages(userId: str, chatContext: str, db: Session = Depends(get_db)):
    user = User.get_by_id(db, userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        chat_context_enum = ChatContextType[chatContext.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid chat context")

    chat = user.get_or_create_chat(db, chat_context_enum)
    messages = chat.get_messages(db)

    if not messages:
        first_message = chat.add_message(db, "Hi Jane, how can I assist you today?", MessageType.SYSTEM)
        messages = [first_message]

    serialized_messages = [
        {
            "id": str(message.id),
            "line_type": message.line_type.value,
            "content": message.content,
            "created_date": message.created_date.isoformat() if message.created_date else None
        } for message in messages
    ]

    return {
        "user": user.name,
        "chat_context": chat_context_enum.value,
        "messages": serialized_messages,
        "details": "all messages by user chat context"
    }

@app.post("/api/users/{userId}/chats/{chatContext}/messages")
async def send_message(userId: str, chatContext: str, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    user = User.get_by_id(db, userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    chat_context_enum = ChatContextType[chatContext.upper()]
    line_type = data.get('line_type')
    if not line_type:
        raise HTTPException(status_code=400, detail="Message line_type missing")
    line_type_enum = MessageType[line_type.upper()]
    
    # Extract the user content
    user_message_content = data.get('content')
    if not user_message_content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    # Find or create the chat with the given context
    chat = user.get_or_create_chat(db, chat_context_enum)
    # Save the user's message
    user_message = chat.add_message(db, user_message_content, line_type_enum)

    generator = CodeGenerator()
    resp, error = generator.run(user_message_content, userId)
    generated_content = "I've finished working and determined that I can't perform this action"

    if resp and not error:
        file = Path(resp)
        file_name = file.name
        new_user_file = UserFile(file_name=file_name, user_id=user.id)
        db.add(new_user_file)
        db.commit()
        db.refresh(new_user_file)
        output_view_url = f"http://localhost:8000/api/users/{userId}/user-files/{new_user_file.id}"
        generated_content = f"I've generated some output. link: {output_view_url}"
    
    # Save the system message
    system_message = chat.add_message(db, generated_content, MessageType.SYSTEM)

    return {
        "user": user.name,
        "chat_context": chat_context_enum.value,
        "details": generated_content
    }

@app.delete("/api/users/{userId}/chats/{chatContext}/messages/{messageId}")
async def delete_message(userId: str, chatContext: str, messageId: str, request: Request, db: Session = Depends(get_db)):
    chat_context_enum = ChatContextType[chatContext.upper()]
    # Check if user exists
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat = db.query(Chat).filter(Chat.user_id == user.id, Chat.context == chat_context_enum).first()
    if not chat:
        raise HTTPException(status_code=422, detail="Something went wrong")
    
    user_message = db.query(Message).filter(Message.id == messageId).first()
    db.delete(user_message)
    db.commit()

    return {
        "user": user.name,
        "chat_context": chat_context_enum.value,
        "details": "Delete success, please refresh messages"
    }

@app.put("/api/users/{userId}/chats/{chatContext}/messages/{messageId}")
async def update_message(userId: str, chatContext: str, messageId: str, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    chat_context_enum = ChatContextType[chatContext.upper()]
    # Check if user exists
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat = db.query(Chat).filter(Chat.user_id == user.id, Chat.context == chat_context_enum).first()
    if not chat:
        raise HTTPException(status_code=422, detail="Something went wrong")
    
    # Check if message exists and belongs to the user and chat
    message = db.query(Message).filter(
        Message.id == messageId,
        Message.chat_id == chat.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Update the message
    new_content = data.get('content')
    if new_content is None:
        raise HTTPException(status_code=400, detail="New message content is required")
    
    message.content = new_content
    db.commit()
    db.refresh(message)

    generator = CodeGenerator()
    resp, error = generator.run(new_content, userId)
    generated_content = "I've finished working and determined that I can't perform this action"

    if resp and not error:
        file = Path(resp)
        file_name = file.name
        new_user_file = UserFile(file_name=file_name, user_id=user.id)
        db.add(new_user_file)
        db.commit()
        db.refresh(new_user_file)
        output_view_url = f"http://localhost:8000/api/users/{userId}/user-files/{new_user_file.id}"
        generated_content = f"I've generated some output. link: {output_view_url}"
    
    # Save the system message
    system_message = chat.add_message(db, generated_content, MessageType.SYSTEM)

    return {
        "user": user.name,
        "chat_context": chat_context_enum.value,
        "message": {
            "id": message.id,
            "content": message.content,
        },
        "details": generated_content
    }

# Serve static files from the output directory
app.mount("/output", StaticFiles(directory="output"), name="output")


# Endpoint to download a generated file
@app.get("/api/users/{userId}/user-files/{userFileId}")
async def get_user_file(userId: str, userFileId: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_file = user.get_file(db, userFileId)  # Assuming user.get_file is defined

    # Construct the file path
    output_dir = Path(os.getcwd()) / 'output' / 'users' / userId
    file_path = output_dir / user_file.file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Serve the file for downloading or embedding
    return FileResponse(file_path)
    