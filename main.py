from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, User, Product, CartItem
import schemas
import auth


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered E-Commerce API")

@app.get("/")
def read_root():
    return {
        "status": "API Operational",
        "project": "E-Commerce Backend"
    }

@app.get("/test-db")
def test_database(db: Session = Depends(get_db)):
    try:
        total_users = db.query(User).count()
        return {
            "status": "Success",
            "message": "Database connection verified and active",
            "registered_users": total_users
        }
    except Exception as e:
        return {
            "status": "Failure",
            "message": f"Database connectivity error: {str(e)}"
        }


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already registered."
        )
    

    hashed_pwd = auth.get_password_hash(user_data.password)
    

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == user_data.email).first()
  
    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
   
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    
    
    access_token = auth.create_access_token(data=token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }