from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import random
import string
from app.database import get_db
from app.models import User, Order, Payment, PaymentStatus, OrderStatus
from app.schemas import PaymentCreate, PaymentResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/payments", tags=["支付管理"])


def generate_payment_no():
    """生成支付单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"PAY{timestamp}{random_str}"


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建支付订单"""
    # 获取订单信息
    result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限支付此订单")
    
    if order.payment_status == PaymentStatus.PAID.value:
        raise HTTPException(status_code=400, detail="订单已支付")
    
    # 创建支付记录
    db_payment = Payment(
        order_id=payment.order_id,
        payment_no=generate_payment_no(),
        payment_method=payment.payment_method,
        amount=order.total_price,
        status=PaymentStatus.PENDING.value
    )
    
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    
    # TODO: 调用第三方支付接口
    # 这里应该调用支付宝、微信支付等第三方API
    
    return db_payment


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取支付详情"""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    # 获取关联订单检查权限
    result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = result.scalar_one_or_none()
    
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限查看此支付记录")
    
    return payment


@router.post("/{payment_id}/callback")
async def payment_callback(
    payment_id: int,
    transaction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """支付回调（模拟）"""
    # 获取支付记录
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    # 更新支付状态
    payment.status = PaymentStatus.PAID.value
    payment.transaction_id = transaction_id
    payment.paid_at = datetime.utcnow()
    
    # 更新订单支付状态
    result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = result.scalar_one_or_none()
    if order:
        order.payment_status = PaymentStatus.PAID.value
        order.status = OrderStatus.CONFIRMED.value
    
    await db.commit()
    
    return {"message": "支付成功"}

