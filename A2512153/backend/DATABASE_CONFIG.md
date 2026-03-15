# 数据库连接配置

## 当前配置

- **数据库类型**: MySQL
- **用户名**: root
- **密码**: asd2003221
- **主机**: localhost
- **端口**: 3306
- **数据库名**: elderly_care
- **字符集**: utf8mb4

## 连接字符串

```
mysql+aiomysql://root:asd2003221@localhost:3306/elderly_care?charset=utf8mb4
```

## 配置位置

### 1. 配置文件（app/config.py）

默认配置已设置，如需修改可直接编辑 `backend/app/config.py`：

```python
DATABASE_URL: str = "mysql+aiomysql://root:asd2003221@localhost:3306/elderly_care?charset=utf8mb4"
```

### 2. 环境变量（.env文件）

在 `backend` 目录下创建 `.env` 文件（可选）：

```env
DATABASE_URL=mysql+aiomysql://root:asd2003221@localhost:3306/elderly_care?charset=utf8mb4
```

如果设置了环境变量，会优先使用环境变量的值。

## 初始化数据库

使用SQL文件初始化数据库：

```bash
mysql -u root -p < backend/init_database.sql
```

或者：

```bash
mysql -u root -p
source /path/to/backend/init_database.sql
```

## 测试连接

```bash
mysql -u root -p -h localhost -P 3306
```

输入密码：`asd2003221`

## 注意事项

1. 确保MySQL服务已启动
2. 确保数据库 `elderly_care` 已创建（SQL文件会自动创建）
3. 确保用户 `root` 有创建数据库的权限
4. 生产环境建议使用专用数据库用户，不要使用root

## 修改密码

如果需要修改数据库密码：

1. 修改 `backend/app/config.py` 中的 `DATABASE_URL`
2. 或修改 `.env` 文件中的 `DATABASE_URL`
3. 重启后端服务

---

最后更新：2025年1月17日

