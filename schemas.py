from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr 
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True  

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    image_url: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    image_url: str | None

    class Config:
        from_attributes = True

      
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse 

    class Config:
        from_attributes = True

        from typing import List


class CartOverviewResponse(BaseModel):
    items: List[CartItemResponse]
    total_price: float

    class Config:
        from_attributes = True