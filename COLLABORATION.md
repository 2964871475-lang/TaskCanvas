# 团队协作指南

## 一、环境准备

### 1. 安装必要工具

- **Git**: https://git-scm.com/downloads
- **Node.js** (v18+): https://nodejs.org/
- **Python** (3.10+): https://www.python.org/
- **VS Code** (推荐): https://code.visualstudio.com/

### 2. 克隆项目

```bash
git clone git@github.com:2964871475-lang/TaskCanvas.git
cd TaskCanvas
```

### 3. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

---

## 二、Git 分支策略

**禁止直接在 main 分支上开发！** 每个人在自己的分支上工作。

### 分支命名规范

```
模块前缀/姓名缩写/功能描述
```

示例：
- `feature/zs/task-drag` — 张三做任务拖拽功能
- `feature/ls/vocab-review` — 李四做单词复习功能
- `bugfix/ww/fix-login` — 王五修复登录bug

### 日常工作流程

```bash
# 1. 确保 main 是最新的
git checkout main
git pull origin main

# 2. 创建自己的分支（只需第一次）
git checkout -b feature/zs/task-drag

# 3. 开发完成后，提交代码
git add .
git commit -m "feat: 实现任务拖拽排序功能"

# 4. 推送自己的分支到远程
git push origin feature/zs/task-drag

# 5. 在 GitHub 上创建 Pull Request (PR)
#    → 打开 github.com → 点击 "Compare & pull request"
#    → 填写标题和描述 → 点击 "Create pull request"
#    → 请其他成员 review 后合并到 main

# 6. 合并后，删除远程分支，本地切回 main
git checkout main
git pull origin main
git branch -d feature/zs/task-drag
```

### 提交信息规范

```
类型: 简短描述

类型包括：
- feat:     新功能
- fix:      修复bug
- docs:     文档更新
- style:    代码格式调整
- refactor: 重构
- test:     测试
- chore:    构建/工具变更
```

---

## 三、模块分工建议

| 成员 | 负责模块 | 后端文件 | 前端文件 |
|------|---------|---------|---------|
| 成员A | 用户与团队 | `routers/users.py` | `views/Login.vue`, `views/Team.vue` |
| 成员B | 任务看板 | `routers/tasks.py` | `views/Tasks.vue`, `components/TaskCard.vue` |
| 成员C | 单词学习 | `routers/vocabulary.py` | `views/Vocabulary.vue`, `components/WordCard.vue` |
| 成员D | 习惯与番茄钟 | `routers/habits.py` | `views/Habits.vue`, `components/PomodoroTimer.vue` |
| 成员E | 数据驾驶舱 | `routers/stats.py` | `views/Dashboard.vue` |

> **注意**: `models.py`、`database.py`、`main.py`、`App.vue` 等公共文件修改前请先在群里沟通！

---

## 四、开发规范

### 后端 (Python)

- 使用 FastAPI 框架，路由文件放在 `app/routers/`
- 数据模型定义在 `models.py`
- 启动方式: `cd backend && python main.py`
- API 文档: http://127.0.0.1:8000/docs

### 前端 (Vue)

- 使用 Vue 3 组合式 API (`<script setup>`)
- 页面放在 `views/`，可复用组件放在 `components/`
- 接口调用统一在 `api/index.js` 中定义
- UI 组件使用 Element Plus
- 启动方式: `cd frontend && npm run dev`

### 遇到冲突怎么办

```bash
# 1. 先切到自己的分支
git checkout feature/zs/task-drag

# 2. 拉取最新的 main
git fetch origin main

# 3. 合并 main 到自己的分支
git merge origin/main

# 4. 如果有冲突，手动解决冲突文件中的 <<<< HEAD / ==== / >>>> 标记
#    保留正确的代码，删除标记符号

# 5. 解决后提交
git add .
git commit -m "merge: 解决与main的冲突"

# 6. 推送
git push origin feature/zs/task-drag
```

---

## 五、常见问题

### Q: 推送时提示 permission denied？
A: 确认你已被添加为仓库协作者，并在 GitHub 上接受了邀请。

### Q: 如何同步其他人的代码？
A: `git pull origin main` 拉取最新代码。

### Q: 不小心直接在 main 上改了代码？
A: 不要提交！执行 `git stash` 暂存修改，然后 `git checkout -b feature/xx/xx` 创建新分支，再 `git stash pop` 恢复修改。

### Q: npm install 报错？
A: 确认 Node.js 版本 >= 18，尝试删除 `node_modules` 和 `package-lock.json` 后重新安装。
