from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import User, ServiceCategory
from app.schemas import ServiceCategoryCreate, ServiceCategoryResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/categories", tags=["服务分类"])


@router.get("/", response_model=List[ServiceCategoryResponse])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取服务分类列表"""
    result = await db.execute(
        select(ServiceCategory)
        .where(ServiceCategory.is_active == True)
        .order_by(ServiceCategory.sort_order)
        .offset(skip)
        .limit(limit)
    )
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}", response_model=ServiceCategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """获取分类详情"""
    result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.post("/", response_model=ServiceCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: ServiceCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建服务分类（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限创建分类")
    
    db_category = ServiceCategory(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=ServiceCategoryResponse)
async def update_category(
    category_id: int,
    category_update: ServiceCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新服务分类（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限修改分类")
    
    result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    update_data = category_update.model_dump()
    for key, value in update_data.items():
        setattr(category, key, value)
    
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除服务分类（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限删除分类")
    
    result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    category.is_active = False
    await db.commit()

