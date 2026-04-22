from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from backend.auth.utils import verify_password, get_password_hash, create_access_token
from backend.db.database import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserAuthRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int

@router.post("/register", response_model=TokenResponse)
async def register(request: UserAuthRequest):
    existing_user = await get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(request.password)
    user_id = await create_user(request.email, hashed_password)
    
    access_token = create_access_token(data={"sub": request.email, "user_id": user_id})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}

@router.post("/login", response_model=TokenResponse)
async def login(request: UserAuthRequest):
    user = await get_user_by_email(request.email)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user["id"]}
