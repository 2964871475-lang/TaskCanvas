# TaskCanvas - 智适应学习任务管理平台

一站式考研学习助手，集成任务管理、单词学习、习惯养成、数据可视化。

## 功能模块

1. **用户与团队管理** - 注册登录、个人档案编辑、创建小组、邀请成员、组内评论
2. **智能任务看板** - 考研倒计时、任务分类(每日/长期/错题)、拖拽排序、优先级筛选、连续打卡、任务评论
3. **单词趣味学习** - 词书管理、手动/批量导入、艾宾浩斯曲线复习、错题本、单词连连看游戏、收藏标星
4. **习惯养成 & 番茄钟** - 自定义习惯、打卡日历、番茄钟(开始/暂停/继续)、小组排行榜
5. **数据可视化驾驶舱** - 任务/单词/番茄钟趋势折线图、掌握度热力图、小组对比柱状图、周报导出(PNG)

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Chart.js + vuedraggable + Pinia |
| 后端 | Python FastAPI + SQLAlchemy + matplotlib |
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
├── backend/                     # FastAPI 后端
│   ├── main.py                  # 入口
│   ├── requirements.txt         # Python 依赖
│   └── app/
│       ├── database.py          # 数据库配置
│       ├── models.py            # 数据模型(12个表)
│       └── routers/
│           ├── users.py         # 用户与团队
│           ├── tasks.py         # 任务看板
│           ├── vocabulary.py    # 单词学习
│           ├── habits.py        # 习惯与番茄钟
│           ├── stats.py         # 数据统计
│           ├── comments.py      # 评论系统
│           └── export.py        # 周报导出
├── frontend/                    # Vue 3 前端
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── stores/user.js       # Pinia 状态管理
│       ├── api/index.js         # 接口封装
│       ├── router/index.js      # 路由(含守卫)
│       ├── components/
│       │   ├── CommentSection.vue   # 评论组件
│       │   ├── WordMatchGame.vue    # 单词连连看
│       │   └── HeatMap.vue          # 热力图
│       └── views/
│           ├── Home.vue         # 首页
│           ├── Login.vue        # 登录注册
│           ├── Tasks.vue        # 任务看板(拖拽)
│           ├── Vocabulary.vue   # 单词学习(连连看)
│           ├── Habits.vue       # 习惯与番茄钟
│           ├── Dashboard.vue    # 数据驾驶舱
│           ├── Team.vue         # 团队管理
│           ├── Profile.vue      # 个人档案
│           └── NotFound.vue     # 404页面
├── COLLABORATION.md             # 团队协作指南
└── README.md
```
