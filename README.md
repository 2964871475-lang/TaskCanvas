# TaskCanvas - 智适应学习任务管理平台

一站式考研学习助手，集成任务管理、单词学习、习惯养成、数据可视化。

## 功能模块

1. **用户与团队管理** - 注册登录、个人档案、小组协作、共享看板
2. **智能任务看板** - 考研倒计时、任务分类、拖拽排序、连续打卡
3. **单词趣味学习** - 艾宾浩斯曲线复习、错题本、单词连连看
4. **习惯养成 & 番茄钟** - 自定义习惯、专注计时、小组排行榜
5. **数据可视化驾驶舱** - 趋势折线图、掌握度热力图、周报导出

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Chart.js |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | SQLite |

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
# API 文档: http://127.0.0.1:8000/docs
```

### 前端

```bash
cd frontend
npm install
npm run dev
# 访问: http://localhost:5173
```

## 项目结构

```
TaskCanvas/
├── backend/                # FastAPI 后端
│   ├── main.py            # 入口
│   ├── requirements.txt
│   └── app/
│       ├── database.py    # 数据库配置
│       ├── models.py      # 数据模型
│       └── routers/       # API 路由
│           ├── users.py       # 用户与团队
│           ├── tasks.py       # 任务看板
│           ├── vocabulary.py  # 单词学习
│           ├── habits.py      # 习惯与番茄钟
│           └── stats.py       # 数据统计
├── frontend/               # Vue 3 前端
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── api/           # 接口封装
│       ├── router/        # 路由
│       ├── views/         # 页面
│       └── components/    # 组件
└── COLLABORATION.md        # 团队协作指南
```
