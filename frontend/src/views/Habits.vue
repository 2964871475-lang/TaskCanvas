<template>
  <div class="habits-page">
    <h1 class="page-title">习惯养成 & 番茄钟</h1>

    <!-- 四个卡片：左列（习惯+排行）+ 右列（番茄钟+历史） -->
    <el-row :gutter="20" class="habits-row">
      <!-- 左列 -->
      <el-col :xs="24" :sm="24" :md="12" class="habits-col">
        <!-- 卡片1: 我的习惯 -->
        <el-card class="habits-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>我的习惯</span>
              <div class="header-actions">
                <span class="progress-text">{{ todayDone }}/{{ habits.length }}</span>
                <el-button type="primary" size="small" @click="showAddHabit = true">+ 新建</el-button>
              </div>
            </div>
          </template>
          <div class="habit-list">
            <div v-for="habit in habits" :key="habit.id" class="habit-item">
              <span class="habit-icon">{{ habit.icon }}</span>
              <div class="habit-info">
                <span class="habit-name">{{ habit.name }}</span>
                <div class="habit-dots">
                  <span v-for="d in 7" :key="d" class="dot" :class="{ done: isDayDone(habit, d) }" :title="dayLabel(d)" />
                </div>
              </div>
              <div class="habit-actions">
                <el-button type="success" size="small" @click="checkin(habit)">打卡</el-button>
                <el-button size="small" text @click="editHabit(habit)">编辑</el-button>
                <el-button type="danger" size="small" text @click="removeHabit(habit)">删除</el-button>
              </div>
            </div>
            <el-empty v-if="!habits.length" description="还没有习惯" :image-size="60" />
          </div>
        </el-card>

        <!-- 卡片2: 专注排行榜 -->
        <el-card class="habits-card" shadow="hover">
          <template #header><span>专注排行榜（本周）</span></template>
          <div class="leaderboard-list">
            <div v-for="(item, i) in leaderboard" :key="item.username" class="leader-item">
              <span class="rank">#{{ i + 1 }}</span>
              <span class="name">{{ item.username }}</span>
              <span class="minutes">{{ item.total_minutes }}分钟</span>
            </div>
            <el-empty v-if="!leaderboard.length" description="暂无数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右列 -->
      <el-col :xs="24" :sm="24" :md="12" class="habits-col">
        <!-- 卡片3: 番茄钟 -->
        <el-card class="habits-card" shadow="hover">
          <template #header><span>番茄钟</span></template>
          <div class="pomodoro">
            <div class="timer-display" :class="{ running: isRunning }">{{ formatTime(timeLeft) }}</div>
            <div class="timer-actions">
              <el-button v-if="!isRunning && !isPaused" type="primary" size="large" @click="startTimer">开始专注</el-button>
              <el-button v-else-if="isRunning" type="warning" size="large" @click="pauseTimer">暂停</el-button>
              <el-button v-if="isPaused" type="primary" size="large" @click="resumeTimer">继续</el-button>
              <el-button v-if="isRunning || isPaused" type="danger" size="large" @click="stopTimer">结束</el-button>
            </div>
            <div class="task-selector" v-if="pendingTasks.length">
              <el-select v-model="selectedTaskId" placeholder="关联任务（可选）" clearable size="small" style="width:240px" :disabled="isRunning || isPaused">
                <el-option v-for="t in pendingTasks" :key="t.id" :label="t.title" :value="t.id" />
              </el-select>
            </div>
            <div class="timer-presets">
              <el-radio-group v-model="duration" :disabled="isRunning || isPaused">
                <el-radio-button :value="25">25分钟</el-radio-button>
                <el-radio-button :value="45">45分钟</el-radio-button>
                <el-radio-button :value="60">60分钟</el-radio-button>
                <el-radio-button :value="0">自定义</el-radio-button>
              </el-radio-group>
              <div v-if="duration === 0" class="custom-time">
                <el-input-number v-model="customDuration" :min="1" :max="180" :step="5" size="small" />
                <span class="custom-label">分钟</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 卡片4: 番茄钟历史 -->
        <el-card class="habits-card" shadow="hover">
          <template #header><span>番茄钟历史</span></template>
          <div class="history-list">
            <div v-for="s in pomodoroHistory" :key="s.id" class="history-item">
              <div>
                <span>{{ s.duration_minutes }}分钟</span>
                <el-tag v-if="s.task_title" size="small" type="info" style="margin-left:8px">{{ s.task_title }}</el-tag>
              </div>
              <span class="history-time">{{ formatDateTime(s.started_at) }}</span>
            </div>
            <el-empty v-if="!pomodoroHistory.length" description="暂无记录" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建/编辑习惯对话框 -->
    <el-dialog v-model="showAddHabit" :title="editingHabit ? '编辑习惯' : '新建习惯'">
      <el-form :model="habitForm">
        <el-form-item label="名称"><el-input v-model="habitForm.name" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="habitForm.icon" style="width:80px" /></el-form-item>
        <el-form-item label="频率">
          <el-radio-group v-model="habitForm.frequency">
            <el-radio value="daily">每天</el-radio>
            <el-radio value="weekly">每周</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="每日目标"><el-input-number v-model="habitForm.target_count" :min="1" :max="10" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddHabit = false">取消</el-button>
        <el-button type="primary" @click="saveHabit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import dayjs from "dayjs";
import { habitApi, taskApi } from "../api";
import { useUserStore } from "../stores/user";

const store = useUserStore();
const pendingTasks = ref([]);
const selectedTaskId = ref(null);
const habits = ref([]);
const leaderboard = ref([]);
const pomodoroHistory = ref([]);
const showAddHabit = ref(false);
const editingHabit = ref(null);
const habitForm = ref({ name: "", icon: "✓", frequency: "daily", target_count: 1 });

const duration = ref(25);
const customDuration = ref(30);
const timeLeft = ref(25 * 60);
const isRunning = ref(false);
const isPaused = ref(false);
let timer = null;
let currentSessionId = null;
const habitRecords = ref({});

// 从 localStorage 恢复番茄钟状态
function restorePomodoro() {
  const saved = localStorage.getItem("pomodoro_state");
  if (!saved) return;
  try {
    const state = JSON.parse(saved);
    if (!state.sessionId) return;
    const elapsed = Math.floor((Date.now() - state.startedAt) / 1000);
    const totalSeconds = state.durationMinutes * 60;
    const remaining = totalSeconds - elapsed;
    if (remaining <= 0) {
      // 已超时，自动完成
      localStorage.removeItem("pomodoro_state");
      habitApi.completePomodoro(state.sessionId).then(() => {
        loadLeaderboard();
        loadPomodoroHistory();
      });
      return;
    }
    currentSessionId = state.sessionId;
    duration.value = state.durationMinutes;
    timeLeft.value = remaining;
    isPaused.value = true;
    ElMessage.info("检测到未完成的番茄钟，已恢复计时");
  } catch { localStorage.removeItem("pomodoro_state"); }
}

function savePomodoroState() {
  if (currentSessionId) {
    localStorage.setItem("pomodoro_state", JSON.stringify({
      sessionId: currentSessionId,
      startedAt: Date.now() - ((duration.value === 0 ? customDuration.value : duration.value) * 60 - timeLeft.value) * 1000,
      durationMinutes: duration.value === 0 ? customDuration.value : duration.value,
    }));
  } else {
    localStorage.removeItem("pomodoro_state");
  }
}

watch(duration, (val) => { if (!isRunning.value && !isPaused.value) timeLeft.value = (val === 0 ? customDuration.value : val) * 60; });
watch(customDuration, (val) => { if (duration.value === 0 && !isRunning.value && !isPaused.value) timeLeft.value = val * 60; });

const todayDone = computed(() => {
  const today = dayjs().format("YYYY-MM-DD");
  return habits.value.filter((h) => {
    const records = habitRecords.value[h.id] || [];
    return records.some((r) => dayjs(r.completed_at).format("YYYY-MM-DD") === today);
  }).length;
});

function formatTime(s) { return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`; }
function formatDateTime(d) { return dayjs(d).format("MM-DD HH:mm"); }
function dayLabel(d) { return ["一", "二", "三", "四", "五", "六", "日"][d - 1]; }
function isDayDone(habit, d) {
  const records = habitRecords.value[habit.id] || [];
  const target = dayjs().subtract(7 - d, "day").format("YYYY-MM-DD");
  return records.some((r) => dayjs(r.completed_at).format("YYYY-MM-DD") === target);
}

async function loadHabits() {
  if (!store.userId) return;
  const { data } = await habitApi.list(store.userId);
  habits.value = data;
  for (const h of data) {
    try {
      const { data: recs } = await habitApi.getRecords(h.id);
      habitRecords.value[h.id] = recs;
    } catch { habitRecords.value[h.id] = []; }
  }
}

async function loadLeaderboard() { try { const { data } = await habitApi.leaderboard(); leaderboard.value = data; } catch {} }
async function loadPomodoroHistory() { if (!store.userId) return; try { const { data } = await habitApi.pomodoroHistory(store.userId); pomodoroHistory.value = data; } catch {} }
async function loadPendingTasks() {
  if (!store.userId) return;
  try {
    const { data } = await taskApi.list(store.userId);
    pendingTasks.value = data.filter(t => t.status !== "done");
  } catch { /* ignore */ }
}

function editHabit(habit) {
  editingHabit.value = habit;
  habitForm.value = { name: habit.name, icon: habit.icon, frequency: habit.frequency, target_count: habit.target_count };
  showAddHabit.value = true;
}

async function saveHabit() {
  if (editingHabit.value) {
    await habitApi.update(editingHabit.value.id, habitForm.value);
  } else {
    await habitApi.create({ ...habitForm.value, user_id: store.userId });
  }
  showAddHabit.value = false;
  editingHabit.value = null;
  habitForm.value = { name: "", icon: "✓", frequency: "daily", target_count: 1 };
  loadHabits();
}

async function removeHabit(habit) {
  await ElMessageBox.confirm("确定删除？", "提示", { type: "warning" });
  await habitApi.delete(habit.id);
  loadHabits();
}

async function checkin(habit) {
  const { data } = await habitApi.checkin(habit.id);
  ElMessage.success(`${habit.name} 打卡成功！${data.today_count}/${data.target}`);
  loadHabits();
}

function startTimer() {
  const mins = duration.value === 0 ? customDuration.value : duration.value;
  if (mins <= 0) { ElMessage.warning("请选择有效的专注时长"); return; }
  timeLeft.value = mins * 60;
  isRunning.value = true;
  isPaused.value = false;
  timer = setInterval(() => { timeLeft.value--; if (timeLeft.value <= 0) completeTimer(); }, 1000);
  habitApi.startPomodoro({ user_id: store.userId, duration_minutes: mins, task_id: selectedTaskId.value || undefined })
    .then(({ data }) => {
      currentSessionId = data.id;
      savePomodoroState();
    });
}

function pauseTimer() {
  isRunning.value = false;
  isPaused.value = true;
  clearInterval(timer);
  savePomodoroState();
}
function resumeTimer() {
  isRunning.value = true;
  isPaused.value = false;
  timer = setInterval(() => { timeLeft.value--; if (timeLeft.value <= 0) completeTimer(); }, 1000);
}

async function stopTimer() { completeTimer(); }

async function completeTimer() {
  clearInterval(timer);
  isRunning.value = false;
  isPaused.value = false;
  if (currentSessionId) {
    try {
      await habitApi.completePomodoro(currentSessionId);
      ElMessage.success("专注完成！");
    } catch {
      ElMessage.warning("保存失败，但番茄钟已结束");
    }
    currentSessionId = null;
    localStorage.removeItem("pomodoro_state");
    loadLeaderboard();
    loadPomodoroHistory();
  }
}

onMounted(() => {
  restorePomodoro();
  loadHabits();
  loadLeaderboard();
  loadPomodoroHistory();
  loadPendingTasks();
});
</script>

<style scoped>
.habits-page { max-width: 1600px; margin: 0 auto; }
.habits-row { align-items: stretch; }
.habits-col { display: flex; flex-direction: column; gap: 16px; }
.habits-card { flex: 1; min-height: 280px; display: flex; flex-direction: column; }

.card-header { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.progress-text { font-weight: 600; color: #409eff; font-size: 14px; }

/* 习惯列表 */
.habit-list { flex: 1; overflow-y: auto; min-height: 150px; }
.habit-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.habit-item:last-child { border-bottom: none; }
.habit-icon { font-size: 24px; width: 36px; text-align: center; flex-shrink: 0; }
.habit-info { flex: 1; min-width: 0; }
.habit-name { font-weight: 500; display: block; margin-bottom: 4px; }
.habit-dots { display: flex; gap: 4px; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: #dcdfe6; }
.dot.done { background: #67c23a; }
.habit-actions { display: flex; gap: 2px; align-items: center; flex-shrink: 0; }

/* 排行榜 */
.leaderboard-list { flex: 1; overflow-y: auto; min-height: 150px; }
.leader-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.leader-item:last-child { border-bottom: none; }
.rank { font-weight: 700; color: #e6a23c; width: 36px; flex-shrink: 0; }
.name { flex: 1; min-width: 0; }
.minutes { color: #909399; flex-shrink: 0; }

/* 番茄钟 */
.pomodoro { text-align: center; padding: 20px; }
.timer-display { font-size: 56px; font-weight: 700; color: #409eff; font-family: monospace; margin-bottom: 20px; }
.timer-display.running { color: #e6a23c; animation: pulse 1s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }
.timer-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 16px; }
.task-selector { margin-bottom: 12px; display: flex; justify-content: center; }
.timer-presets { margin-top: 12px; }
.custom-time { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; }
.custom-label { color: #909399; font-size: 14px; }

/* 番茄钟历史 */
.history-list { flex: 1; overflow-y: auto; min-height: 150px; }
.history-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.history-item:last-child { border-bottom: none; }
.history-time { color: #909399; }

@media (max-width: 768px) {
  .habits-page { max-width: 100%; }
  .habits-card { min-height: auto; }
  .habit-actions { flex-wrap: wrap; }
  .timer-display { font-size: 42px; }
  .timer-presets :deep(.el-radio-button__inner) { padding: 6px 10px; font-size: 12px; }
}
</style>
