from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import User, Address
from app.schemas import AddressCreate, AddressUpdate, AddressResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/addresses", tags=["地址管理"])


@router.get("/", response_model=List[AddressResponse])
async def get_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户地址列表"""
    result = await db.execute(
        select(Address)
        .where(Address.user_id == current_user.id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    addresses = result.scalars().all()
    return addresses


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取地址详情"""
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalar_one_or_none()
    
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    if address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限访问此地址")
    
    return address


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建地址"""
    # 如果设置为默认地址，取消其他默认地址
    if address.is_default:
        result = await db.execute(
            select(Address).where(
                Address.user_id == current_user.id,
                Address.is_default == True
            )
        )
        for addr in result.scalars():
            addr.is_default = False
    
    db_address = Address(
        **address.model_dump(),
        user_id=current_user.id
    )
    db.add(db_address)
    await db.commit()
    await db.refresh(db_address)
    return db_address


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_update: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新地址"""
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalar_one_or_none()
    
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    if address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此地址")
    
    # 如果设置为默认地址，取消其他默认地址
    if address_update.is_default:
        result = await db.execute(
            select(Address).where(
                Address.user_id == current_user.id,
                Address.is_default == True,
                Address.id != address_id
            )
        )
        for addr in result.scalars():
            addr.is_default = False
    
    update_data = address_update.model_dump()
    for key, value in update_data.items():
        setattr(address, key, value)
    
    await db.commit()
    await db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除地址"""
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalar_one_or_none()
    
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    if address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此地址")
    
    await db.delete(address)
    await db.commit()

