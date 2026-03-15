# SQL数据库初始化说明

## 文件说明

`init_database.sql` - 完整的数据库初始化SQL脚本，包含表结构和示例数据。

## 使用方法

### 方法1：使用MySQL命令行

```bash
# 登录MySQL
mysql -u root -p

# 执行SQL文件
source /path/to/init_database.sql

# 或者直接导入
mysql -u root -p < init_database.sql
```

### 方法2：使用MySQL Workbench

1. 打开MySQL Workbench
2. 连接到MySQL服务器
3. 打开 `init_database.sql` 文件
4. 执行整个脚本（点击执行按钮）

### 方法3：使用DBeaver等数据库工具

1. 连接到MySQL服务器
2. 打开SQL编辑器
3. 导入并执行 `init_database.sql` 文件

## 包含的内容

### 1. 数据库结构
- ✅ 7张核心数据表
- ✅ 完整的索引和外键约束
- ✅ 使用 utf8mb4 字符集

### 2. 示例数据

#### 用户数据（7个）
- **管理员**：1个
  - 用户名：`admin`，密码：`password123`
- **服务提供商**：3个
  - `provider1` - 张护理
  - `provider2` - 李医生
  - `provider3` - 王厨师
- **老年人**：2个
  - `elderly1` - 刘大爷
  - `elderly2` - 陈奶奶
- **家属**：1个
  - `family1` - 刘先生

#### 服务分类（8个）
1. 居家护理 🏠
2. 医疗服务 ⚕️
3. 餐饮服务 🍱
4. 家政服务 🧹
5. 陪伴服务 👥
6. 康复理疗 💆
7. 心理咨询 🧠
8. 紧急救助 🚨

#### 服务数据（14个）
涵盖所有分类的示例服务，包括：
- 专业居家护理服务
- 健康体检服务
- 营养配餐服务
- 家庭深度清洁
- 聊天陪伴服务
- 专业按摩服务
- 心理健康咨询
- 24小时紧急响应
- 等等...

#### 其他数据
- **地址**：3个示例地址
- **订单**：4个示例订单（不同状态）
- **支付**：3个支付记录
- **评价**：3个用户评价

## 默认账号

### 管理员账号
- **用户名**：`admin`
- **密码**：`password123`
- **邮箱**：`admin@example.com`

### 测试账号
所有测试账号的密码都是：`password123`

- 服务提供商：`provider1`, `provider2`, `provider3`
- 老年人：`elderly1`, `elderly2`
- 家属：`family1`

## 注意事项

### ⚠️ 密码说明
SQL文件中的密码是示例密码（`password123`），实际使用时：
1. 应该使用bcrypt加密后的密码
2. 密码已使用bcrypt加密，可直接使用
3. 或者使用应用的用户注册功能创建新用户

### ⚠️ 生产环境
- 不要在生产环境直接使用示例数据
- 修改所有默认密码
- 删除或修改示例数据
- 使用强密码策略

### ⚠️ 字符集
确保MySQL使用 `utf8mb4` 字符集，以支持中文和emoji表情。

## 验证安装

执行SQL后，可以运行以下查询验证：

```sql
-- 检查表是否创建
SHOW TABLES;

-- 检查用户数据
SELECT id, username, role, is_active FROM users;

-- 检查服务数据
SELECT id, title, price, rating FROM services;

-- 检查订单数据
SELECT order_no, status, payment_status, total_price FROM orders;
```

## 重置数据库

如果需要清空所有数据重新开始：

```sql
-- 删除所有表（注意：会删除所有数据）
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS service_categories;
DROP TABLE IF EXISTS users;

-- 然后重新执行 init_database.sql
```

## 与Python脚本的区别

- **init_database.sql**：纯SQL脚本，可以直接在MySQL中执行，包含完整的表结构和示例数据

使用方法：
- 直接执行SQL文件：`mysql -u root -p < init_database.sql`
- 或在MySQL命令行中执行：`source init_database.sql`

## 常见问题

### Q: 执行SQL时提示字符集错误
A: 确保MySQL版本 >= 8.0，并支持utf8mb4字符集

### Q: 外键约束错误
A: 确保按顺序执行，先创建被引用的表，再创建引用表

### Q: 密码无法登录
A: SQL中的密码是示例，实际应用需要使用bcrypt加密的密码

---

**最后更新**：2025年1月17日

