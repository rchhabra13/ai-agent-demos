from datetime import datetime
from pydantic import BaseModel


class SessionData(BaseModel):
    session_id: str
    github_token: str
    username: str
    email: str | None = None
    expires_at: datetime
