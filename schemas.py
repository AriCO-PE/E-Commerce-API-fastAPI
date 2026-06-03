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

    # Schema for product creation input (Day 10 preview)
class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    image_url: str | None = None

# Schema for product API responses
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    image_url: str | None

    class Config:
        from_attributes = True