from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from app.database import get_db
from app.models import User, Service, ServiceCategory
from app.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/services", tags=["服务管理"])


@router.get("/", response_model=List[ServiceResponse])
async def get_services(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取服务列表（支持搜索和筛选）"""
    query = select(Service).where(Service.is_active == True)
    
    # 分类筛选
    if category_id:
        query = query.where(Service.category_id == category_id)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Service.title.ilike(f"%{keyword}%"),
                Service.description.ilike(f"%{keyword}%")
            )
        )
    
    # 价格筛选
    if min_price is not None:
        query = query.where(Service.price >= min_price)
    if max_price is not None:
        query = query.where(Service.price <= max_price)
    
    query = query.offset(skip).limit(limit).order_by(Service.created_at.desc())
    result = await db.execute(query)
    services = result.scalars().all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    """获取服务详情"""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    return service


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建服务"""
    # 检查分类是否存在
    result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.id == service.category_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="服务分类不存在")
    
    db_service = Service(
        **service.model_dump(),
        provider_id=current_user.id
    )
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新服务"""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    
    if service.provider_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限修改此服务")
    
    update_data = service_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)
    
    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除服务（软删除）"""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    
    if service.provider_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限删除此服务")
    
    service.is_active = False
    await db.commit()

