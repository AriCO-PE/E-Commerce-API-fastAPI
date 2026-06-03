from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import engine, get_db
from models import Base, User, Product, CartItem
import schemas
import auth
import stripe


from dependencies import get_current_user, check_admin_role


# Load environment variables from the .env file
load_dotenv()

# Securely fetch keys from the environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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




@app.post("/cart/add", response_model=schemas.CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {item_data.product_id} does not exist."
        )
    
    
    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {product.stock} items available."
        )

  
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item_data.product_id
    ).first()

    if existing_item:
       
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Combined quantity exceeds available stock."
            )
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        
        new_cart_item = CartItem(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        return new_cart_item
    


@app.get("/cart", response_model=schemas.CartOverviewResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    
    total = sum(item.quantity * item.product.price for item in cart_items)
    
    return {
        "items": cart_items,
        "total_price": round(total, 2)
    }


@app.delete("/cart", status_code=status.HTTP_200_OK)
def clear_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete(synchronize_session=False)
    db.commit()
    
    return {
        "status": "Success",
        "message": "Your shopping cart has been successfully emptied."
    }

@app.post("/checkout", status_code=status.HTTP_200_OK)
def checkout_and_pay(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your shopping cart is empty. Cannot proceed to checkout."
        )
        
    
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    
  
    amount_in_cents = int(total_price * 100)
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            metadata={
                "user_id": str(current_user.id),
                "email": current_user.email
            }
        )
        
     
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete(synchronize_session=False)
        db.commit()
        
      
        return {
            "status": "Success",
            "message": "Payment intent created successfully. Cart has been cleared.",
            "total_amount_usd": round(total_price, 2),
            "client_secret": payment_intent.client_secret
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe Gateway Error: {str(e)}"
        )