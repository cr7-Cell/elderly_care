from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List
from datetime import datetime
import random
import string
from app.database import get_db
from app.models import User, Order, Service, OrderStatus, PaymentStatus
from app.schemas import OrderCreate, OrderUpdate, OrderResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/orders", tags=["订单管理"])


def generate_order_no():
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"ORD{timestamp}{random_str}"


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单列表"""
    query = select(Order)
    
    # 普通用户只能查看自己的订单
    if current_user.role != "admin":
        query = query.where(
            or_(
                Order.user_id == current_user.id,
                Order.provider_id == current_user.id
            )
        )
    
    # 状态筛选
    if status:
        query = query.where(Order.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单详情"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 权限检查
    if (current_user.role != "admin" and 
        order.user_id != current_user.id and 
        order.provider_id != current_user.id):
        raise HTTPException(status_code=403, detail="无权限查看此订单")
    
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建订单"""
    # 获取服务信息
    result = await db.execute(select(Service).where(Service.id == order.service_id))
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    
    if not service.is_active:
        raise HTTPException(status_code=400, detail="服务已下架")
    
    # 计算总价
    total_price = service.price * order.quantity
    
    # 创建订单
    db_order = Order(
        order_no=generate_order_no(),
        user_id=current_user.id,
        service_id=order.service_id,
        provider_id=service.provider_id,
        quantity=order.quantity,
        total_price=total_price,
        appointment_date=order.appointment_date,
        address_id=order.address_id,
        remark=order.remark,
        status=OrderStatus.PENDING.value,
        payment_status=PaymentStatus.PENDING.value
    )
    
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 权限检查
    if (current_user.role != "admin" and 
        order.user_id != current_user.id and 
        order.provider_id != current_user.id):
        raise HTTPException(status_code=403, detail="无权限修改此订单")
    
    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)
    
    await db.commit()
    await db.refresh(order)
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限取消此订单")
    
    if order.status not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
        raise HTTPException(status_code=400, detail="当前状态不允许取消订单")
    
    order.status = OrderStatus.CANCELLED.value
    await db.commit()
    await db.refresh(order)
    return order

