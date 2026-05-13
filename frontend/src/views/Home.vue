<template>
  <div class="home">
    <div class="hero" @mousemove="onMouseMove" ref="heroRef">
      <div class="hero-glow" :style="glowStyle"></div>
      <div class="hero-content">
        <h1 class="animated-title">TaskCanvas</h1>
        <p class="subtitle">智适应学习任务管理平台</p>
        <p class="desc">任务管理 + 单词学习 + 习惯养成 + 数据可视化，一站式考研学习助手</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="goTo('/tasks')">开始使用</el-button>
          <el-button size="large" round @click="goTo('/dashboard')">查看数据</el-button>
        </div>
        <div class="hero-stats">
          <div class="stat-item" v-for="s in stats" :key="s.label">
            <span class="stat-num">{{ s.value }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>
      </div>
      <div class="floating-shapes">
        <span v-for="i in 6" :key="i" class="shape" :class="'shape-' + i"></span>
      </div>
    </div>
    <!-- 公告栏 -->
    <div v-if="store.isLoggedIn && announcements.length" class="announce-section">
      <div class="announce-header">
        <el-icon><Bell /></el-icon>
        <span>平台公告</span>
      </div>
      <el-carousel :interval="5000" height="80px" indicator-position="none" arrow="never" v-if="announcements.length > 1">
        <el-carousel-item v-for="a in announcements" :key="a.id">
          <div class="announce-item" @click="showAnnDetail(a)">
            <div class="announce-title">{{ a.title }}</div>
            <div class="announce-meta">
              <el-tag v-if="a.team_id" size="small" type="info">{{ a.team_name }}</el-tag>
              <el-tag v-else size="small" type="danger">全局</el-tag>
              <span class="announce-time">{{ fmtTime(a.created_at) }}</span>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
      <div v-else class="announce-item" @click="showAnnDetail(announcements[0])">
        <div class="announce-title">{{ announcements[0].title }}</div>
        <div class="announce-meta">
          <el-tag v-if="announcements[0].team_id" size="small" type="info">{{ announcements[0].team_name }}</el-tag>
          <el-tag v-else size="small" type="danger">全局</el-tag>
          <span class="announce-time">{{ fmtTime(announcements[0].created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 公告详情弹窗 -->
    <el-dialog v-model="showDetail" :title="detailAnn?.title || '公告详情'" width="500px">
      <div v-if="detailAnn">
        <div class="detail-meta">
          <el-tag v-if="detailAnn.team_id" size="small" type="info">{{ detailAnn.team_name }}</el-tag>
          <el-tag v-else size="small" type="danger">全局公告</el-tag>
          <span>发布者：{{ detailAnn.publisher_name }}</span>
          <span>{{ fmtTime(detailAnn.created_at) }}</span>
        </div>
        <el-divider />
        <p style="white-space:pre-wrap;line-height:1.8;color:var(--text-regular)">{{ detailAnn.content }}</p>
      </div>
    </el-dialog>

    <!-- 今日进度 & 复习提醒 -->
    <div v-if="store.isLoggedIn" class="progress-section">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="24" :md="16">
          <div class="progress-card">
            <div class="progress-header">
              <span class="progress-title">今日学习进度</span>
              <el-button text type="primary" size="small" @click="showGoalDialog = true">设置目标</el-button>
            </div>
            <div class="progress-items">
              <div class="prog-item">
                <div class="prog-label"><span class="prog-icon">📋</span> 完成任务</div>
                <el-progress :percentage="goalPercent('tasks')" :stroke-width="18" :format="() => `${progress.tasks_done}/${progress.goals?.tasks?.target || '-'}`" />
              </div>
              <div class="prog-item">
                <div class="prog-label"><span class="prog-icon">⏱️</span> 学习时长</div>
                <el-progress :percentage="goalPercent('minutes')" :stroke-width="18" :color="'#e6a23c'" :format="() => `${progress.study_minutes}/${progress.goals?.minutes?.target || '-'}min`" />
              </div>
              <div class="prog-item">
                <div class="prog-label"><span class="prog-icon">📚</span> 学习单词</div>
                <el-progress :percentage="goalPercent('words')" :stroke-width="18" :color="'#67c23a'" :format="() => `${progress.words_studied}/${progress.goals?.words?.target || '-'}`" />
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <div class="review-card" @click="goTo('/vocabulary')">
            <div class="review-icon">📖</div>
            <div class="review-info">
              <div class="review-count">{{ reviewCount }}</div>
              <div class="review-label">个单词待复习</div>
            </div>
            <div class="review-action">
              <el-button type="warning" size="small" round>去复习</el-button>
            </div>
          </div>
          <div class="pomodoro-card" @click="goTo('/habits')">
            <div class="pomo-icon">🍅</div>
            <div class="pomo-info">
              <div class="pomo-count">{{ progress.pomodoro_count || 0 }}</div>
              <div class="pomo-label">今日番茄钟</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 设置目标弹窗 -->
    <el-dialog v-model="showGoalDialog" title="设置学习目标" width="450px">
      <el-form label-width="100px">
        <el-form-item label="每日任务数">
          <el-input-number v-model="goalForm.tasks" :min="0" :max="50" />
        </el-form-item>
        <el-form-item label="学习时长(min)">
          <el-input-number v-model="goalForm.minutes" :min="0" :max="720" :step="30" />
        </el-form-item>
        <el-form-item label="学习单词数">
          <el-input-number v-model="goalForm.words" :min="0" :max="200" :step="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGoalDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGoals">保存</el-button>
      </template>
    </el-dialog>

    <div class="features">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="6" v-for="(f, idx) in features" :key="f.title">
          <el-card shadow="hover" class="feature-card" :style="{ animationDelay: idx * 0.1 + 's' }" @click="goTo(f.path)">
            <div class="feature-icon float-icon">{{ f.icon }}</div>
            <h3>{{ f.title }}</h3>
            <p>{{ f.desc }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Bell } from "@element-plus/icons-vue";
import dayjs from "dayjs";
import { userApi, statsApi, vocabApi } from "../api";
import { useUserStore } from "../stores/user";

const router = useRouter();
const store = useUserStore();
const heroRef = ref(null);
const announcements = ref([]);
const showDetail = ref(false);
const detailAnn = ref(null);
const progress = ref({});
const reviewCount = ref(0);
const showGoalDialog = ref(false);
const goalForm = ref({ tasks: 5, minutes: 120, words: 30 });

function fmtTime(d) { return d ? dayjs(d).format("MM-DD HH:mm") : ""; }
function showAnnDetail(a) { detailAnn.value = a; showDetail.value = true; }

function goalPercent(type) {
  const goal = progress.value.goals?.[type]?.target || 0;
  if (!goal) return 0;
  const actual = type === "tasks" ? progress.value.tasks_done : type === "minutes" ? progress.value.study_minutes : progress.value.words_studied;
  return Math.min(100, Math.round((actual / goal) * 100));
}

async function loadAnnouncements() {
  if (!store.isLoggedIn) return;
  try {
    const { data } = await userApi.getAnnouncements(store.userId);
    announcements.value = data;
  } catch { /* ignore */ }
}

async function loadProgress() {
  if (!store.isLoggedIn) return;
  try {
    const [pRes, rRes] = await Promise.all([
      statsApi.dailyProgress(store.userId),
      vocabApi.getReviewCount(store.userId),
    ]);
    progress.value = pRes.data;
    reviewCount.value = rRes.data.count;
    // 填充目标表单
    const g = pRes.data.goals || {};
    goalForm.value = {
      tasks: g.tasks?.target || 5,
      minutes: g.minutes?.target || 120,
      words: g.words?.target || 30,
    };
  } catch { /* ignore */ }
}

async function saveGoals() {
  try {
    await Promise.all([
      statsApi.createGoal({ user_id: store.userId, goal_type: "tasks", target_value: goalForm.value.tasks, period: "daily" }),
      statsApi.createGoal({ user_id: store.userId, goal_type: "minutes", target_value: goalForm.value.minutes, period: "daily" }),
      statsApi.createGoal({ user_id: store.userId, goal_type: "words", target_value: goalForm.value.words, period: "daily" }),
    ]);
    showGoalDialog.value = false;
    loadProgress();
  } catch { /* ignore */ }
}
const mouseX = ref(50);
const mouseY = ref(50);

const glowStyle = computed(() => ({
  background: `radial-gradient(circle 300px at ${mouseX.value}% ${mouseY.value}%, rgba(255,255,255,0.15), transparent)`,
}));

function onMouseMove(e) {
  if (!heroRef.value) return;
  const rect = heroRef.value.getBoundingClientRect();
  mouseX.value = ((e.clientX - rect.left) / rect.width) * 100;
  mouseY.value = ((e.clientY - rect.top) / rect.height) * 100;
}

function goTo(path) {
  router.push(store.isLoggedIn ? path : "/login");
}

const stats = [
  { value: "4", label: "核心模块" },
  { value: "12", label: "数据表" },
  { value: "∞", label: "可能" },
];

const features = [
  { icon: "📋", title: "智能任务看板", desc: "拖拽排序、优先级管理、考研倒计时、连续打卡", path: "/tasks" },
  { icon: "📚", title: "单词趣味学习", desc: "艾宾浩斯曲线复习、错题本、单词连连看", path: "/vocabulary" },
  { icon: "⏱️", title: "番茄钟 & 习惯", desc: "专注计时、习惯打卡、小组排行榜", path: "/habits" },
  { icon: "📊", title: "数据驾驶舱", desc: "学习趋势图、掌握度热力图、周报导出", path: "/dashboard" },
];

onMounted(() => { loadAnnouncements(); loadProgress(); });
</script>

<style scoped>
.home { max-width: 1200px; margin: 0 auto; }

.hero {
  text-align: center;
  padding: 60px 40px;
  margin-bottom: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius-lg);
  color: #fff;
  position: relative;
  overflow: hidden;
}

/* 鼠标跟随光效 */
.hero-glow {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  transition: background 0.3s ease;
}

/* 浮动装饰 */
.floating-shapes { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  animation: floatUp linear infinite;
}
.shape-1 { width: 80px; height: 80px; left: 10%; bottom: -80px; animation-duration: 12s; animation-delay: 0s; }
.shape-2 { width: 50px; height: 50px; left: 30%; bottom: -50px; animation-duration: 10s; animation-delay: 2s; }
.shape-3 { width: 120px; height: 120px; left: 55%; bottom: -120px; animation-duration: 15s; animation-delay: 1s; }
.shape-4 { width: 40px; height: 40px; left: 75%; bottom: -40px; animation-duration: 9s; animation-delay: 3s; }
.shape-5 { width: 60px; height: 60px; left: 85%; bottom: -60px; animation-duration: 11s; animation-delay: 0.5s; }
.shape-6 { width: 90px; height: 90px; left: 45%; bottom: -90px; animation-duration: 14s; animation-delay: 4s; }

@keyframes floatUp {
  0% { transform: translateY(0) rotate(0deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-600px) rotate(360deg); opacity: 0; }
}

.hero-content { position: relative; z-index: 2; }

/* 渐变色标题动画 */
.animated-title {
  font-size: 52px;
  margin-bottom: 12px;
  letter-spacing: 2px;
  background: linear-gradient(90deg, #fff, #a8edea, #fed6e3, #fff);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: titleShimmer 4s ease-in-out infinite;
}

@keyframes titleShimmer {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.subtitle { font-size: 22px; opacity: 0.9; margin-bottom: 12px; }
.desc { font-size: 16px; opacity: 0.75; margin-bottom: 28px; }
.hero-actions { display: flex; gap: 16px; justify-content: center; margin-bottom: 36px; }
.hero-actions .el-button { padding: 12px 32px; font-size: 16px; }

.hero-stats { display: flex; gap: 48px; justify-content: center; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-num { font-size: 32px; font-weight: 700; }
.stat-label { font-size: 14px; opacity: 0.7; margin-top: 4px; }

.features { margin-top: 0; }
.feature-card {
  text-align: center;
  padding: 24px 20px;
  cursor: pointer;
  height: 100%;
  border-radius: var(--radius-md);
  animation: cardFadeIn 0.6s ease backwards;
}

@keyframes cardFadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.feature-card :deep(.el-card__body) { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.feature-icon { font-size: 44px; margin-bottom: 16px; }

/* 图标浮动动画 */
.float-icon { animation: iconFloat 3s ease-in-out infinite; }
.feature-card:nth-child(2) .float-icon { animation-delay: 0.5s; }
.feature-card:nth-child(3) .float-icon { animation-delay: 1s; }
.feature-card:nth-child(4) .float-icon { animation-delay: 1.5s; }

@keyframes iconFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.feature-card h3 { margin-bottom: 10px; color: var(--text-primary); min-height: 24px; font-size: 18px; }
.feature-card p { color: var(--text-secondary); font-size: 14px; min-height: 40px; line-height: 1.6; }

/* 公告栏 */
.announce-section {
  margin-bottom: 28px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fff7e6 0%, #fff1f0 100%);
  border-radius: var(--radius-md);
  border: 1px solid #ffe58f;
}
.announce-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: #d46b08; margin-bottom: 10px;
}
.announce-item { cursor: pointer; padding: 4px 0; }
.announce-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }
.announce-meta { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--text-secondary); }
.announce-time { margin-left: auto; }

.detail-meta { display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--text-secondary); }

/* 进度卡片 */
.progress-section { margin-bottom: 28px; }
.progress-card {
  padding: 20px; background: #fff;
  border-radius: var(--radius-md); box-shadow: var(--shadow-sm);
}
.progress-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}
.progress-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.progress-items { display: flex; flex-direction: column; gap: 14px; }
.prog-item { }
.prog-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
.prog-icon { font-size: 16px; }

.review-card {
  display: flex; align-items: center; gap: 16px;
  padding: 20px; background: linear-gradient(135deg, #fff7e6 0%, #fff1f0 100%);
  border-radius: var(--radius-md); border: 1px solid #ffe58f;
  cursor: pointer; transition: transform 0.2s;
}
.review-card:hover { transform: translateY(-2px); }
.review-icon { font-size: 36px; }
.review-count { font-size: 28px; font-weight: 700; color: #d46b08; }
.review-label { font-size: 13px; color: #d46b08; }
.review-action { margin-left: auto; }

.pomodoro-card {
  display: flex; align-items: center; gap: 16px;
  padding: 16px 20px; margin-top: 12px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-radius: var(--radius-md); border: 1px solid #c2e7b0;
  cursor: pointer; transition: transform 0.2s;
}
.pomodoro-card:hover { transform: translateY(-2px); }
.pomo-icon { font-size: 30px; }
.pomo-count { font-size: 24px; font-weight: 700; color: #529b2e; }
.pomo-label { font-size: 13px; color: #529b2e; }

@media (max-width: 768px) {
  .hero { padding: 40px 20px; margin-bottom: 24px; }
  .animated-title { font-size: 36px; }
  .subtitle { font-size: 18px; }
  .desc { font-size: 14px; margin-bottom: 20px; }
  .hero-actions .el-button { padding: 10px 24px; font-size: 14px; }
  .hero-stats { gap: 24px; }
  .stat-num { font-size: 24px; }
  .feature-card { padding: 16px 12px; }
  .feature-icon { font-size: 32px; margin-bottom: 10px; }
  .feature-card h3 { font-size: 15px; }
  .feature-card p { font-size: 13px; min-height: auto; }
  .review-card { padding: 16px; }
  .pomodoro-card { padding: 12px 16px; }
}
@media (max-width: 480px) {
  .hero { padding: 30px 16px; }
  .animated-title { font-size: 28px; }
  .subtitle { font-size: 16px; }
  .hero-actions { flex-direction: column; align-items: center; gap: 10px; }
  .hero-stats { gap: 16px; }
  .stat-num { font-size: 20px; }
  .stat-label { font-size: 12px; }
}
</style>
