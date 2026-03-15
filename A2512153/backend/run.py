# 导入必要模块
import uvicorn
# 从app/main.py导入FastAPI应用实例（核心）
from app.main import app

# 直接启动服务器（最简配置）
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",          # 要启动的FastAPI实例
        host="127.0.0.1", # 仅本地访问（更安全，适合测试）
        port=8000,        # 监听端口
        reload=True       # 开发环境热重载（改代码自动重启）
    )