from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SERVICE_PROVIDER = "service_provider"
    ELDERLY = "elderly"
    FAMILY_MEMBER = "family_member"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar = Column(String(255))
    role = Column(String(20), default=UserRole.ELDERLY.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    reviews = relationship("Review", back_populates="user")
    addresses = relationship("Address", back_populates="user")


class ServiceCategory(Base):
    __tablename__ = "service_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    services = relationship("Service", back_populates="category")


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("service_categories.id"))
    provider_id = Column(Integer, ForeignKey("users.id"))
    price = Column(Float, nullable=False)
    unit = Column(String(20))  # 单位：次、小时、天等
    image = Column(String(255))
    images = Column(Text)  # JSON格式存储多张图片
    service_time = Column(String(100))  # 服务时长
    location = Column(String(255))
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("ServiceCategory", back_populates="services")
    provider = relationship("User", foreign_keys=[provider_id])
    orders = relationship("Order", back_populates="service")
    reviews = relationship("Review", back_populates="service")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    provider_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), default=OrderStatus.PENDING.value)
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)
    appointment_date = Column(DateTime)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="orders", foreign_keys=[user_id])
    service = relationship("Service", back_populates="orders")
    provider = relationship("User", foreign_keys=[provider_id])
    address = relationship("Address")
    payment = relationship("Payment", back_populates="order", uselist=False)


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    payment_no = Column(String(50), unique=True, index=True, nullable=False)
    payment_method = Column(String(50))  # alipay, wechat, stripe等
    amount = Column(Float, nullable=False)
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    transaction_id = Column(String(100))  # 第三方支付交易号
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    order = relationship("Order", back_populates="payment")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Integer, nullable=False)  # 1-5星
    comment = Column(Text)
    images = Column(Text)  # JSON格式存储评价图片
    reply = Column(Text)  # 商家回复
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="reviews")
    service = relationship("Service", back_populates="reviews")


class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contact_name = Column(String(50), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    province = Column(String(50))
    city = Column(String(50))
    district = Column(String(50))
    detail_address = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="addresses")

