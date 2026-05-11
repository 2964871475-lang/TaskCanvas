<template>
  <div class="home">
    <!-- Hero section -->
    <div class="hero">
      <div class="hero-content">
        <h1 class="hero-title">TaskCanvas</h1>
        <p class="hero-subtitle">智适应学习任务管理平台</p>
        <p class="hero-desc">任务管理 + 单词学习 + 习惯养成 + 数据可视化，一站式考研学习助手</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="goTo('/tasks')">
            <el-icon><List /></el-icon>
            开始使用
          </el-button>
          <el-button size="large" @click="goTo('/dashboard')">
            <el-icon><DataLine /></el-icon>
            查看数据
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <div class="hero-illustration">
          <div class="illustration-card card-1">
            <span class="card-icon">📋</span>
            <span class="card-text">任务管理</span>
          </div>
          <div class="illustration-card card-2">
            <span class="card-icon">📚</span>
            <span class="card-text">单词学习</span>
          </div>
          <div class="illustration-card card-3">
            <span class="card-icon">⏱️</span>
            <span class="card-text">专注计时</span>
          </div>
          <div class="illustration-card card-4">
            <span class="card-icon">📊</span>
            <span class="card-text">数据统计</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Features section -->
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div
          v-for="f in features"
          :key="f.title"
          class="feature-card"
        >
          <div class="feature-icon-wrapper">
            <span class="feature-icon">{{ f.icon }}</span>
          </div>
          <h3 class="feature-title">{{ f.title }}</h3>
          <p class="feature-desc">{{ f.desc }}</p>
          <ul class="feature-list">
            <li v-for="item in f.items" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Stats section -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-item" v-for="stat in stats" :key="stat.label">
          <div class="stat-number">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- CTA section -->
    <div class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">开始高效学习之旅</h2>
        <p class="cta-desc">加入 TaskCanvas，让学习更有条理，让进步看得见</p>
        <el-button type="primary" size="large" @click="goTo('/tasks')">
          立即开始
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { List, DataLine } from "@element-plus/icons-vue";

const router = useRouter();
const store = useUserStore();

function goTo(path) {
  router.push(store.isLoggedIn ? path : "/login");
}

const features = [
  {
    icon: "📋",
    title: "智能任务看板",
    desc: "可视化任务管理，让学习计划一目了然",
    items: ["拖拽排序，灵活调整优先级", "考研倒计时，把握每个关键节点", "连续打卡记录，培养学习习惯"]
  },
  {
    icon: "📚",
    title: "单词趣味学习",
    desc: "科学记忆方法，高效掌握考研词汇",
    items: ["艾宾浩斯曲线，智能安排复习", "错题本功能，重点攻克薄弱词汇", "单词连连看，寓教于乐"]
  },
  {
    icon: "⏱️",
    title: "番茄钟 & 习惯",
    desc: "专注计时工具，养成良好学习习惯",
    items: ["番茄工作法，提升专注力", "习惯打卡，坚持每日学习", "小组排行榜，互相激励"]
  },
  {
    icon: "📊",
    title: "数据驾驶舱",
    desc: "学习数据可视化，清晰掌握学习进度",
    items: ["学习趋势图，了解学习状态", "掌握度热力图，发现薄弱环节", "周报导出，总结学习成果"]
  }
];

const stats = [
  { value: "10,000+", label: "考研词汇" },
  { value: "98%", label: "用户满意度" },
  { value: "50万+", label: "学习记录" },
  { value: "24/7", label: "随时可用" }
];
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

/* Hero section */
.hero {
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 40px 0 60px;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 12px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 20px;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 16px;
}

.hero-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-actions .el-button {
  padding: 12px 28px;
  font-size: 16px;
}

/* Hero illustration */
.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
}

.hero-illustration {
  position: relative;
  width: 360px;
  height: 300px;
}

.illustration-card {
  position: absolute;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-md);
  transition: transform 0.3s ease;
}

.illustration-card:hover {
  transform: translateY(-4px);
}

.card-icon {
  font-size: 28px;
}

.card-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.card-1 {
  top: 0;
  left: 20px;
}

.card-2 {
  top: 70px;
  right: 0;
}

.card-3 {
  bottom: 70px;
  left: 0;
}

.card-4 {
  bottom: 0;
  right: 20px;
}

/* Features section */
.features-section {
  padding: 60px 0;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 32px 24px;
  border: 1px solid var(--border-lighter);
  transition: all 0.3s ease;
}

.feature-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
}

.feature-icon-wrapper {
  width: 56px;
  height: 56px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.feature-icon {
  font-size: 28px;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.feature-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.6;
}

.feature-list {
  list-style: none;
  padding: 0;
}

.feature-list li {
  font-size: 14px;
  color: var(--text-regular);
  padding: 6px 0;
  padding-left: 20px;
  position: relative;
}

.feature-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: var(--success);
  font-weight: 600;
}

/* Stats section */
.stats-section {
  padding: 40px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-item {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 24px;
  text-align: center;
  border: 1px solid var(--border-lighter);
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* CTA section */
.cta-section {
  padding: 60px 0;
}

.cta-content {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border-radius: var(--radius-lg);
  padding: 48px;
  text-align: center;
  color: #fff;
}

.cta-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 12px;
}

.cta-desc {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 32px;
}

.cta-section .el-button {
  padding: 12px 36px;
  font-size: 16px;
  background: #fff !important;
  color: var(--primary) !important;
  border-color: #fff !important;
}

.cta-section .el-button:hover {
  background: var(--bg-hover) !important;
}

/* Responsive */
@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    gap: 40px;
    text-align: center;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-illustration {
    width: 280px;
    height: 240px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .cta-content {
    padding: 32px 24px;
  }
}
</style>
