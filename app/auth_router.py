from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.orm import Session
from .config import CLIENT_ID, CLIENT_SECRET, get_db
from .models import User

# Create an APIRouter instance
router = APIRouter()

# Initialize OAuth
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

# Templating system
templates = Jinja2Templates(directory="templates")

# Login route
@router.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)

# OAuth callback route
@router.get('/auth')
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

# Logout route
@router.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    response = RedirectResponse('/')
    response.delete_cookie(key="session")
    return response
