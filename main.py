from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import engine, get_db
from models import Base, User, Product, CartItem
import schemas
import auth


from dependencies import get_current_user, check_admin_role

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
    new_user = User(email=user_data.email, hashed_password=hashed_pwd)
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




@app.get("/users/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/admin/dashboard")
def get_admin_dashboard(admin_user: User = Depends(check_admin_role)):
    return {
        "status": "Success",
        "message": f"Welcome back Admin {admin_user.email}! Access to secret operations granted."
    }



@app.get("/products", response_model=List[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@app.get("/products/{id}", response_model=schemas.ProductResponse)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {id} was not found in our catalog."
        )
    return product


@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin_role) 
):
 
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        image_url=product_data.image_url
    )
    
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product