# Hubaooo's Warehouse Backend

产品拆解与虚拟组装网站的第一版后端。

## 已实现

- 分类：数码设备、钟表、汽车等
- 产品：名称、品牌、简介、封面、整机 3D 模型
- 零件：说明、功能原理、材质、独立 3D 模型、初始变换参数
- 装配关系：零件之间的先后/连接关系和操作提示
- Swagger / OpenAPI 文档
- SQLite 本地开发；可切换 PostgreSQL

## 本地启动

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
alembic upgrade head
python -m app.create_admin
python -m app.seed
uvicorn app.main:app --reload
```

浏览器打开：

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health
- 产品列表：http://127.0.0.1:8000/api/v1/products

## 配置

复制 `.env.example` 为 `.env`。默认数据库是项目根目录的 `warehouse.db`。上线时把 `DATABASE_URL` 设置为 PostgreSQL 连接地址。

## 主要接口

| 方法 | 地址 | 用途 |
|---|---|---|
| GET | `/api/v1/categories` | 分类列表 |
| POST | `/api/v1/categories` | 新增分类 |
| GET | `/api/v1/products` | 产品列表 |
| GET | `/api/v1/products/{slug}` | 产品拆解完整数据 |
| POST | `/api/v1/products` | 新增产品 |
| POST | `/api/v1/products/{id}/parts` | 新增零件 |
| POST | `/api/v1/products/{id}/connections` | 新增装配关系 |
| POST | `/api/v1/assets` | 上传图片或 GLB 模型 |

所有写入、修改和删除接口都需要管理员 Bearer Token。先运行
`python -m app.create_admin` 创建管理员，再在 `/docs` 的 **Authorize** 中登录。

本地上传的文件保存在 `uploads/`，默认上限为 50 MB。上线时将替换为对象存储，
避免服务器重启或重新部署时丢失素材。

## 接下来建议

1. 管理员登录和内容管理后台
2. GLB/图片文件直传对象存储
3. 装配步骤、卡扣点、碰撞规则和完成判定
4. 搜索、收藏与学习进度
5. Alembic 数据库迁移和正式部署
