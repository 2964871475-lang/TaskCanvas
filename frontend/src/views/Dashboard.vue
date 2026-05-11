<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title">数据可视化驾驶舱</h1>
      <el-button type="primary" @click="exportReport"><el-icon><Download /></el-icon> 导出周报</el-button>
    </div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="6" v-for="s in statCards" :key="s.label">
        <el-card shadow="hover"><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card><template #header>近7天任务完成趋势</template><div class="chart-container"><Line v-if="taskChartData" :data="taskChartData" :options="chartOpts" /></div></el-card>
      </el-col>
      <el-col :span="12">
        <el-card><template #header>近7天单词学习趋势</template><div class="chart-container"><Line v-if="wordChartData" :data="wordChartData" :options="chartOpts" /></div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card><template #header>近7天番茄钟专注时长</template><div class="chart-container"><Bar v-if="pomodoroData" :data="pomodoroData" :options="chartOpts" /></div></el-card>
      </el-col>
      <el-col :span="12">
        <el-card><template #header>单词掌握度分布</template><div class="chart-container"><Doughnut v-if="masteryData" :data="masteryData" /></div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card><template #header>学习活跃度热力图</template><HeatMap :data="heatmapData" :weeks="12" /></el-card>
      </el-col>
      <el-col :span="12">
        <el-card><template #header>习惯打卡统计</template>
          <div v-for="h in habitStats" :key="h.habit_id" class="habit-stat-item">
            <span class="hs-icon">{{ h.icon }}</span>
            <span class="hs-name">{{ h.name }}</span>
            <el-progress :percentage="Math.min(100, Math.round(h.total_records / 30 * 100))" style="flex:1" />
            <span class="hs-count">{{ h.total_records }}次</span>
          </div>
          <el-empty v-if="!habitStats.length" description="暂无习惯数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-row v-if="teamComparison.length" :gutter="16" style="margin-top:16px">
      <el-col :span="24">
        <el-card><template #header>小组成员学习对比（本周）</template>
          <div class="chart-container"><Bar :data="teamChartData" :options="chartOpts" /></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Line, Bar, Doughnut } from "vue-chartjs";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from "chart.js";
import { statsApi, exportApi } from "../api";
import { useUserStore } from "../stores/user";
import HeatMap from "../components/HeatMap.vue";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler);

const store = useUserStore();
const overview = ref(null);
const weeklyTasks = ref([]);
const weeklyWords = ref([]);
const weeklyPomodoro = ref([]);
const masteryHeatmap = ref([]);
const habitStats = ref([]);
const teamComparison = ref([]);
const heatmapData = ref([]);
const chartOpts = { responsive: true, maintainAspectRatio: false };

const statCards = computed(() => overview.value ? [
  { label: "总任务", value: overview.value.total_tasks },
  { label: "完成率", value: overview.value.completion_rate + "%" },
  { label: "今日学习", value: overview.value.today_study_minutes + "分钟" },
  { label: "已掌握单词", value: `${overview.value.mastered_words}/${overview.value.total_words}` },
] : []);

const taskChartData = computed(() => weeklyTasks.value.length ? {
  labels: weeklyTasks.value.map((d) => d.date),
  datasets: [{ label: "完成任务数", data: weeklyTasks.value.map((d) => d.count), borderColor: "#409eff", backgroundColor: "rgba(64,158,255,0.1)", fill: true, tension: 0.3 }],
} : null);

const wordChartData = computed(() => weeklyWords.value.length ? {
  labels: weeklyWords.value.map((d) => d.date),
  datasets: [{ label: "学习单词数", data: weeklyWords.value.map((d) => d.count), borderColor: "#67c23a", backgroundColor: "rgba(103,194,58,0.1)", fill: true, tension: 0.3 }],
} : null);

const pomodoroData = computed(() => weeklyPomodoro.value.length ? {
  labels: weeklyPomodoro.value.map((d) => d.date),
  datasets: [{ label: "专注时长(分钟)", data: weeklyPomodoro.value.map((d) => d.minutes), backgroundColor: "#e6a23c" }],
} : null);

const masteryData = computed(() => masteryHeatmap.value.length ? {
  labels: masteryHeatmap.value.map((d) => d.range),
  datasets: [{ data: masteryHeatmap.value.map((d) => d.count), backgroundColor: ["#f56c6c", "#e6a23c", "#409eff", "#67c23a", "#00b894"] }],
} : null);

const teamChartData = computed(() => teamComparison.value.length ? {
  labels: teamComparison.value.map((d) => d.username),
  datasets: [
    { label: "完成任务", data: teamComparison.value.map((d) => d.tasks_done), backgroundColor: "#409eff" },
    { label: "学习单词", data: teamComparison.value.map((d) => d.words_learned), backgroundColor: "#67c23a" },
    { label: "番茄钟(分钟)", data: teamComparison.value.map((d) => d.pomodoro_minutes), backgroundColor: "#e6a23c" },
  ],
} : null);

async function exportReport() {
  try {
    const res = await exportApi.weeklyReport(store.userId);
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url; a.download = "weekly_report.png"; a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("周报已下载");
  } catch { ElMessage.error("导出失败"); }
}

onMounted(async () => {
  if (!store.userId) return;
  const [ov, wt, wm, wp, mh, hs] = await Promise.all([
    statsApi.overview(store.userId), statsApi.weeklyTasks(store.userId),
    statsApi.weeklyWords(store.userId), statsApi.weeklyPomodoro(store.userId),
    statsApi.masteryHeatmap(store.userId), statsApi.habitStreak(store.userId),
  ]);
  overview.value = ov.data;
  weeklyTasks.value = wt.data;
  weeklyWords.value = wm.data;
  weeklyPomodoro.value = wp.data;
  masteryHeatmap.value = mh.data;
  habitStats.value = hs.data;

  // 热力图数据：合并任务+单词学习
  const merged = {};
  wt.data.forEach((d) => { merged[d.date] = (merged[d.date] || 0) + d.count; });
  wm.data.forEach((d) => { merged[d.date] = (merged[d.date] || 0) + d.count; });
  heatmapData.value = Object.entries(merged).map(([date, count]) => ({ date, count }));

  // 小组对比（如果有团队）
  try {
    const teams = await (await import("../api")).userApi.getTeams(store.userId);
    if (teams.data.length) {
      const tc = await statsApi.teamComparison(teams.data[0].id);
      teamComparison.value = tc.data;
    }
  } catch {}
});
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.stat-cards .stat-value { font-size: 28px; font-weight: 700; color: #409eff; }
.stat-label { color: #909399; margin-top: 4px; }
.chart-container { height: 250px; }
.habit-stat-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.hs-icon { font-size: 20px; }
.hs-name { width: 80px; }
.hs-count { color: #909399; font-size: 13px; }
</style>
