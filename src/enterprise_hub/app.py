import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from enterprise_hub.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from enterprise_hub.database import Base, engine, get_db
from enterprise_hub.integration import dispatch_webhook_event
from enterprise_hub.models import AuditLog, User
from enterprise_hub.schemas import (
    AuditLogCreate,
    AuditLogResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Enterprise Production Hub API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", tags=["System"])
def health_check():
    return {"status": "healthy", "database": "connected"}


@app.post(
    "/api/v1/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="member",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(data={"sub": user.email, "role": user.role})
    return TokenResponse(access_token=token)


@app.get("/api/v1/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post(
    "/api/v1/audit",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit_record(
    log: AuditLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    audit_entry = AuditLog(
        user_id=current_user.id,
        action=log.action,
        details=log.details,
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)

    # Trigger external asynchronous integration
    await dispatch_webhook_event(
        log.action, {"user": current_user.email, "id": audit_entry.id}
    )

    return audit_entry


@app.get("/api/v1/audit", response_model=list[AuditLogResponse])
def list_audit_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(AuditLog).filter(AuditLog.user_id == current_user.id).all()


# Serve UI frontend if compiled
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("enterprise_hub.app:app", host="0.0.0.0", port=8000, reload=False)
