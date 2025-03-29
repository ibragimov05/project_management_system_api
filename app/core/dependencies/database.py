from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.base import SESSION_LOCAL


# Create a DB dependency for getting the session
def get_db():
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


DB_DEPENDENCY = Annotated[Session, Depends(get_db)]
