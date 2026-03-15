"""
测试数据库连接脚本
用于诊断数据库连接问题
"""
import asyncio
from app.database import engine
from app.config import settings
from sqlalchemy import text

async def test_connection():
    """测试数据库连接"""
    print(f"数据库URL: {settings.DATABASE_URL}")
    print("正在测试数据库连接...")
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✓ 数据库连接成功: {row[0]}")
            
            # 测试查询users表
            result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✓ 用户表查询成功，共有 {count} 个用户")
            
            # 测试查询admin用户
            result = await conn.execute(text("SELECT id, username, role FROM users WHERE username = 'admin'"))
            user = result.fetchone()
            if user:
                print(f"✓ 找到管理员用户: ID={user[0]}, 用户名={user[1]}, 角色={user[2]}")
            else:
                print("✗ 未找到管理员用户")
                
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())

