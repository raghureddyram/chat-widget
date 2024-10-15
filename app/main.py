from fastapi import FastAPI, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.agents.code_generator import CodeGenerator
from app.models.chat import ChatContextType
from app.models.message import MessageType
from .auth_router import router as auth_router
from .models import User, Message, Chat
from .config import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
    
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        chat_context_enum = ChatContextType[chatContext.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid chat context")

    # Try to fetch the chat, create if it doesn't exist
    try:
        chat = db.query(Chat).filter(
            Chat.user_id == user.id,
            Chat.context == chat_context_enum
        ).first()

        if not chat:
            chat = Chat(user_id=user.id, context=chat_context_enum)
            db.add(chat)
            db.commit()
            db.refresh(chat)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

    # Fetch messages tied to the chat
    messages = db.query(Message).filter(Message.chat_id == chat.id).all()

    # If the chat has no messages, create a default message
    if not messages:
        try:
            first_message = Message(
                chat_id=chat.id,
                content="Hi Jane, how can I assist you today?",
                line_type="SYSTEM"
            )
            db.add(first_message)
            db.commit()
            db.refresh(first_message)
            messages = [first_message]
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error creating default message")

    
    # Serialize messages
    serialized_messages = [
        {
            "id": str(message.id),
            "line_type": message.line_type.value,
            "content": message.content,
            "created_date": message.created_date.isoformat() if message.created_date else None
        } for message in messages
    ]

    # Return the user's messages
    return {
        "user": user.name,
        "chat_context": chat_context_enum.value,
        "messages": serialized_messages
    }

@app.post("/api/users/{userId}/chats/{chatContext}/messages")
async def send_message(userId: str, chatContext: str, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    chat_context_enum = ChatContextType[chatContext.upper()]
    line_type = data.get('line_type')
    if not line_type:
        raise HTTPException(status_code=400, detail="Message line_type missing")
    line_type_enum = MessageType[line_type.upper()]
    
    # Extract the user content
    user_message_content = data.get('content')
    if not user_message_content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    # Check if user exists
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find or create the chat with the given context
    chat = db.query(Chat).filter(Chat.user_id == user.id, Chat.context == chat_context_enum).first()
    if not chat:
        chat = Chat(user_id=user.id, context=chat_context_enum)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    # Save the user's message
    user_message = Message(
        chat_id=chat.id,
        content=user_message_content,
        line_type=line_type_enum
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Generate the system's response
    system_message_content = f"I see that you said: {user_message_content}. Let me work on this..."
    
    # Save the system message
    system_message = Message(
        chat_id=chat.id,
        content=system_message_content,
        line_type=MessageType["SYSTEM"]
    )
    db.add(system_message)
    db.commit()

    # generator = CodeGenerator()
    # resp, error = generator.run(user_message_content)
    # generated_content = "I've finished working and determined that I can't perform this action"

    # if not error and resp:
    #     # messages_url = f"http://localhost:8000/api/users/{userId}/chats/{chatContext}/messages"
    #     generated_content = f"I've generated some output. Please check dummy_url"
    
    # # Save the system message
    # system_message = Message(
    #     chat_id=chat.id,
    #     content=generated_content,
    #     line_type=MessageType["SYSTEM"]
    # )
    # db.add(system_message)
    # db.commit()

    serialized_messages = [
        {
            "id": str(message.id),
            "line_type": message.line_type.value,
            "content": message.content,
            "created_date": message.created_date.isoformat() if message.created_date else None
        } for message in [user_message, system_message]
    ]
    
    return {
        "user": user.name,
        "chat_context": chat_context_enum.value,
        "messages": serialized_messages
    }
    