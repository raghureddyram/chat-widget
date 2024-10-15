import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app, get_db
from ..models import Base
from ..models.chat import ChatContextType
from ..models.message import MessageType
import os

# PostgreSQL database URL for testing
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgresql:@localhost:5432/testdb")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up a TestClient
client = TestClient(app)

# Override the `get_db` dependency for tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_send_message(db):
    user_id = "test_user"
    chat_context = ChatContextType.ONBOARDING.value
    message_data = {
        "line_type": MessageType.USER.value,
        "content": "Hello, this is a test message"
    }

    response = client.post(f"/api/users/{user_id}/chats/{chat_context}/messages", json=message_data)

    assert response.status_code == 200
    response_json = response.json()
    assert "user" in response_json
    assert "chat_context" in response_json
    assert "details" in response_json

    assert response_json["chat_context"] == chat_context
    assert isinstance(response_json["details"], str)