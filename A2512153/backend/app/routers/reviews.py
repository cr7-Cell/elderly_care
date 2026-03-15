from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models import User, Review, Order, Service, OrderStatus
from app.schemas import ReviewCreate, ReviewResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/reviews", tags=["评价管理"])


@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    service_id: int = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取评价列表"""
    query = select(Review)
    
    if service_id:
        query = query.where(Review.service_id == service_id)
    
    query = query.offset(skip).limit(limit).order_by(Review.created_at.desc())
    result = await db.execute(query)
    reviews = result.scalars().all()
    return reviews


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建评价"""
    # 检查订单是否存在且已完成
    result = await db.execute(select(Order).where(Order.id == review.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限评价此订单")
    
    if order.status != OrderStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="订单未完成，暂不能评价")
    
    # 检查是否已评价
    result = await db.execute(
        select(Review).where(Review.order_id == review.order_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="订单已评价")
    
    # 创建评价
    db_review = Review(
        user_id=current_user.id,
        service_id=review.service_id,
        order_id=review.order_id,
        rating=review.rating,
        comment=review.comment,
        images=review.images,
        is_anonymous=review.is_anonymous
    )
    
    db.add(db_review)
    
    # 更新服务评分和评价数
    result = await db.execute(select(Service).where(Service.id == review.service_id))
    service = result.scalar_one_or_none()
    if service:
        # 计算新的平均评分
        result = await db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.service_id == review.service_id)
        )
        avg_rating, count = result.one()
        
        service.rating = float(avg_rating) if avg_rating else 0.0
        service.review_count = count + 1
    
    await db.commit()
    await db.refresh(db_review)
    return db_review


@router.put("/{review_id}/reply")
async def reply_review(
    review_id: int,
    reply: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """商家回复评价"""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    
    # 检查权限（服务提供者）
    result = await db.execute(select(Service).where(Service.id == review.service_id))
    service = result.scalar_one_or_none()
    
    if service.provider_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限回复此评价")
    
    review.reply = reply
    await db.commit()
    
    return {"message": "回复成功"}

