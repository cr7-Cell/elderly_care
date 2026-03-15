from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# 枚举类型
class UserRole(str, Enum):
    ADMIN = "admin"
    SERVICE_PROVIDER = "service_provider"
    ELDERLY = "elderly"
    FAMILY_MEMBER = "family_member"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


# 用户相关Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.ELDERLY


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# 服务分类Schema
class ServiceCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0


class ServiceCategoryCreate(ServiceCategoryBase):
    pass


class ServiceCategoryResponse(ServiceCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# 服务Schema
class ServiceBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: int
    price: float
    unit: Optional[str] = "次"
    image: Optional[str] = None
    images: Optional[str] = None
    service_time: Optional[str] = None
    location: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    image: Optional[str] = None
    images: Optional[str] = None
    service_time: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    provider_id: int
    rating: float
    review_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 订单Schema
class OrderBase(BaseModel):
    service_id: int
    quantity: int = 1
    appointment_date: datetime
    address_id: int
    remark: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    appointment_date: Optional[datetime] = None
    remark: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    order_no: str
    user_id: int
    provider_id: int
    total_price: float
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 支付Schema
class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_no: str
    payment_method: str
    amount: float
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# 评价Schema
class ReviewBase(BaseModel):
    service_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    images: Optional[str] = None
    is_anonymous: bool = False


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    reply: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# 地址Schema
class AddressBase(BaseModel):
    contact_name: str
    contact_phone: str
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: str
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 分页响应
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[dict]

