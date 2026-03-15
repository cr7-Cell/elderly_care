from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 数据库配置（MySQL）
    DATABASE_URL: str = "mysql+aiomysql://root:123456@localhost:3306/elderly_care?charset=utf8mb4"
    
    # Redis配置（减少缓存）
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 5  # 减少Redis连接数
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 支付配置
    STRIPE_API_KEY: str = ""
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()

