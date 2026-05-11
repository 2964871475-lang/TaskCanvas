<template>
  <div class="habits-page">
    <h1 class="page-title">习惯养成 & 番茄钟</h1>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的习惯</span>
              <el-button type="primary" size="small" @click="showAddHabit = true">+ 新建</el-button>
            </div>
          </template>
          <div v-for="habit in habits" :key="habit.id" class="habit-item">
            <span class="habit-icon">{{ habit.icon }}</span>
            <span class="habit-name">{{ habit.name }}</span>
            <el-button type="success" size="small" @click="checkin(habit)">打卡</el-button>
          </div>
          <el-empty v-if="!habits.length" description="还没有习惯，点击新建" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>番茄钟</template>
          <div class="pomodoro">
            <div class="timer-display">{{ formatTime(timeLeft) }}</div>
            <div class="timer-actions">
              <el-button v-if="!isRunning" type="primary" size="large" @click="startTimer">开始专注</el-button>
              <el-button v-else type="danger" size="large" @click="stopTimer">停止</el-button>
            </div>
            <div class="timer-presets">
              <el-radio-group v-model="duration" :disabled="isRunning">
                <el-radio-button :value="25">25分钟</el-radio-button>
                <el-radio-button :value="45">45分钟</el-radio-button>
                <el-radio-button :value="60">60分钟</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </el-card>
        <el-card style="margin-top: 16px">
          <template #header>专注排行榜（本周）</template>
          <div v-for="(item, i) in leaderboard" :key="item.username" class="leader-item">
            <span class="rank">#{{ i + 1 }}</span>
            <span class="name">{{ item.username }}</span>
            <span class="minutes">{{ item.total_minutes }}分钟</span>
          </div>
          <el-empty v-if="!leaderboard.length" description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showAddHabit" title="新建习惯">
      <el-form :model="newHabit">
        <el-form-item label="名称"><el-input v-model="newHabit.name" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="newHabit.icon" style="width:80px" /></el-form-item>
        <el-form-item label="频率">
          <el-radio-group v-model="newHabit.frequency">
            <el-radio value="daily">每天</el-radio>
            <el-radio value="weekly">每周</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddHabit = false">取消</el-button>
        <el-button type="primary" @click="createHabit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { habitApi } from "../api";

const habits = ref([]);
const leaderboard = ref([]);
const showAddHabit = ref(false);
const newHabit = ref({ name: "", icon: "✓", frequency: "daily" });

const duration = ref(25);
const timeLeft = ref(25 * 60);
const isRunning = ref(false);
let timer = null;
let currentSessionId = null;

function getUser() {
  return JSON.parse(localStorage.getItem("user") || "{}");
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

async function loadHabits() {
  const user = getUser();
  if (!user.id) return;
  const { data } = await habitApi.list(user.id);
  habits.value = data;
}

async function loadLeaderboard() {
  const { data } = await habitApi.leaderboard();
  leaderboard.value = data;
}

async function createHabit() {
  const user = getUser();
  await habitApi.create({ ...newHabit.value, user_id: user.id });
  showAddHabit.value = false;
  loadHabits();
}

async function checkin(habit) {
  const { data } = await habitApi.checkin(habit.id);
  ElMessage.success(`${habit.name} 打卡成功！今日 ${data.today_count}/${data.target}`);
}

async function startTimer() {
  timeLeft.value = duration.value * 60;
  isRunning.value = true;
  const user = getUser();
  const { data } = await habitApi.startPomodoro({ user_id: user.id, duration_minutes: duration.value });
  currentSessionId = data.id;

  timer = setInterval(() => {
    timeLeft.value--;
    if (timeLeft.value <= 0) {
      completeTimer();
    }
  }, 1000);
}

async function stopTimer() {
  completeTimer();
}

async function completeTimer() {
  clearInterval(timer);
  isRunning.value = false;
  if (currentSessionId) {
    await habitApi.completePomodoro(currentSessionId);
    ElMessage.success("专注完成！");
    currentSessionId = null;
    loadLeaderboard();
  }
}

onMounted(() => {
  loadHabits();
  loadLeaderboard();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.habit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
.habit-icon {
  font-size: 24px;
}
.habit-name {
  flex: 1;
}
.pomodoro {
  text-align: center;
  padding: 20px;
}
.timer-display {
  font-size: 64px;
  font-weight: 700;
  color: #409eff;
  font-family: monospace;
  margin-bottom: 20px;
}
.timer-actions {
  margin-bottom: 16px;
}
.timer-presets {
  margin-top: 12px;
}
.leader-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}
.rank {
  font-weight: 700;
  color: #e6a23c;
  width: 40px;
}
.name {
  flex: 1;
}
.minutes {
  color: #909399;
}
</style>
