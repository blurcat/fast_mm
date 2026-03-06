# Ops Middle Platform (Fast MM)

Ops Middle Platform 是一个现代化的运维中台管理系统，旨在提供高效的资产管理（CMDB）、权限控制（RBAC）和系统审计功能。项目采用前后端分离架构，基于 FastAPI 和 React (Ant Design Pro) 构建。

## ✨ 主要功能

- **🔐 权限管理 (RBAC)**
  - 基于角色的访问控制
  - 动态权限分配（菜单级、按钮级）
  - 用户、角色、权限的灵活配置

- **📋 菜单管理**
  - 动态菜单生成
  - 菜单排序与层级管理
  - 自动路由配置

- **💻 资产管理 (CMDB)**
  - IT 资产的全生命周期管理
  - 资产详情查看与编辑
  - 物理位置与区域管理
  - 资产变更审计

- **📝 审计日志**
  - 全局操作日志记录
  - 记录操作人、IP、时间、变更详情
  - 支持日志查询与详情查看

- **📊 仪表盘**
  - 系统概览与统计
  - 数据可视化展示

## 🛠 技术栈

### Backend (后端)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Cache**: [Redis](https://redis.io/)
- **Authentication**: JWT (JSON Web Tokens)
- **Migration**: Alembic

### Frontend (前端)
- **Framework**: [React 18](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **UI Component**: [Ant Design Pro](https://procomponents.ant.design/)
- **Language**: TypeScript
- **State Management**: Redux Toolkit / React Context

## 🚀 快速开始

详细部署文档请参考 [DEPLOY.md](./DEPLOY.md)。

### 本地开发

1. **环境准备**
   - Python 3.12+
   - Node.js 18+
   - PostgreSQL & Redis

2. **后端启动**
   ```bash
   # 创建虚拟环境
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 数据库迁移
   alembic upgrade head
   
   # 启动服务
   python -m app.main
   ```

3. **前端启动**
   ```bash
   cd web
   npm install
   npm run dev
   ```

### Docker 部署

一键启动所有服务（数据库、缓存、后端、前端）：

```bash
docker-compose up -d --build
```

访问地址：
- 前端页面: http://localhost
- 后端 API: http://localhost/api/v1/docs

## 📂 项目结构

```
fast_mm/
├── app/                  # 后端应用源码
│   ├── api/              # API 路由与控制器
│   ├── core/             # 核心配置、安全、数据库连接
│   ├── models/           # SQLAlchemy 数据模型
│   └── schemas/          # Pydantic 数据验证模型
├── web/                  # 前端应用源码 (React)
│   ├── src/
│   │   ├── pages/        # 页面组件
│   │   ├── services/     # API 请求服务
│   │   └── components/   # 公共组件
├── alembic/              # 数据库迁移脚本
├── docs/                 # 项目文档
├── DEPLOY.md             # 部署文档
├── docker-compose.yml    # Docker 编排文件
└── requirements.txt      # Python 依赖列表
```

## 📄 License

MIT License
