from fastapi import FastAPI, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from .auth_router import router as auth_router
from .models import User, Message, Chat
from .config import get_db
from sqlalchemy.orm import Session

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


@app.get("/api/users/{userId}/messages")
def get_user_messages(userId: str, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    chat = db.query(Chat).filter(Chat.user_id == user.id).first()

    if not chat:
        chat = Chat(user_id=user.id, title="Default chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # Fetch messages tied to the user
    messages = db.query(Message).filter(Message.chat_id == chat.id).all()

    # If the user has no messages for their chat, return the default message
    if not messages:
        messages = [{"type": "bot", "text": "Hi Jane, how can I assist you today?"}]
        return {"messages": messages}

    # Return the user's messages
    return {"user": user.name, "messages": messages}

# Send message endpoint
@app.post("/api/users/{userId}/messages")
async def send_message(request: Request):
    data = await request.json()
    user_message = data['message']
    # open ai call or code generator to create document
    response_message = f"I see that you said: {user_message}"
    return {"reply": response_message}
