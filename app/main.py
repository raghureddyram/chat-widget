from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from .config import CLIENT_ID, CLIENT_SECRET, SessionLocal
from fastapi.staticfiles import StaticFiles
from .models import User
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

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth'
    }
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')

    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )


@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@app.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )
    user_info = token.get('userinfo')
    if user_info:
        # Check if the user exists in the database by email
        user = db.query(User).filter(User.email == user_info['email']).first()

        # If user doesn't exist, create a new one
        if not user:
            user = User(name=user_info['name'], email=user_info['email'])
            db.add(user)
            db.commit()
            db.refresh(user)

        # Store the user info in the session
        request.session['user'] = {'id': str(user.id), 'name': user.name, 'email': user.email}
    
    return RedirectResponse('http://localhost:3000')


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    response = RedirectResponse('/')
    response.delete_cookie(key="session")
    return response

# ----------------------------
@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )

# ----------------------------

@app.get("/api/session")
def get_session(request: Request):
    user = request.session.get('user')
    if user:
        return {"user": user}
    return {"user": None}