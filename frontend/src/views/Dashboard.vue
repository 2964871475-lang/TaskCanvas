<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title">数据可视化驾驶舱</h1>
      <div class="header-actions">
        <el-button @click="loadDailyReport">日报</el-button>
        <el-button @click="loadMonthlyReport">月报</el-button>
        <el-button type="primary" @click="exportReport"><el-icon><Download /></el-icon> 导出周报</el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="12" :sm="12" :md="6" v-for="s in statCards" :key="s.label">
        <el-card shadow="hover" class="stat-card" :style="{ borderTop: `3px solid ${s.color}` }">
          <div class="stat-icon" :style="{ background: s.color + '15', color: s.color }">{{ s.icon }}</div>
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row" style="margin-top:16px">
      <el-col :xs="24" :sm="24" :md="12" class="chart-col">
        <el-card class="chart-card"><template #header>近7天任务完成趋势</template><div class="chart-container"><Line v-if="taskChartData" :data="taskChartData" :options="chartOpts" /></div></el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" class="chart-col">
        <el-card class="chart-card"><template #header>近7天单词学习趋势</template><div class="chart-container"><Line v-if="wordChartData" :data="wordChartData" :options="chartOpts" /></div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row" style="margin-top:16px">
      <el-col :xs="24" :sm="24" :md="12" class="chart-col">
        <el-card class="chart-card"><template #header>近7天番茄钟专注时长</template><div class="chart-container"><Bar v-if="pomodoroData" :data="pomodoroData" :options="chartOpts" /></div></el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" class="chart-col">
        <el-card class="chart-card"><template #header>单词掌握度分布</template><div class="chart-container"><Doughnut v-if="masteryData" :data="masteryData" /></div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row" style="margin-top:16px">
      <el-col :xs="24" :sm="24" :md="12" class="chart-col">
        <el-card class="chart-card"><template #header>学习活跃度热力图</template><HeatMap :data="heatmapData" :weeks="12" /></el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" class="chart-col">
        <el-card class="chart-card"><template #header>习惯打卡统计</template>
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

    <!-- 学习报告弹窗 -->
    <el-dialog v-model="showReport" :title="reportTitle" width="700px">
      <div v-if="reportType === 'daily' && dailyReport" class="report-content">
        <div class="report-date">{{ dailyReport.date }}</div>
        <div class="report-grid">
          <div class="report-metric">
            <div class="rm-value" style="color:#409eff">{{ dailyReport.tasks_completed.length }}</div>
            <div class="rm-label">完成任务</div>
          </div>
          <div class="report-metric">
            <div class="rm-value" style="color:#e6a23c">{{ dailyReport.study_minutes }}</div>
            <div class="rm-label">学习分钟</div>
          </div>
          <div class="report-metric">
            <div class="rm-value" style="color:#67c23a">{{ dailyReport.words_studied }}</div>
            <div class="rm-label">学习单词</div>
          </div>
          <div class="report-metric">
            <div class="rm-value" style="color:#f56c6c">{{ dailyReport.pomodoro_count }}</div>
            <div class="rm-label">番茄钟</div>
          </div>
        </div>
        <div v-if="dailyReport.goal_progress.length" class="report-section">
          <h4>目标完成</h4>
          <div v-for="g in dailyReport.goal_progress" :key="g.type" class="goal-row">
            <span>{{ goalLabel(g.type) }}: {{ g.actual }}/{{ g.target }}</span>
            <el-tag :type="g.achieved ? 'success' : 'danger'" size="small">{{ g.achieved ? '达成' : '未达成' }}</el-tag>
          </div>
        </div>
        <div v-if="dailyReport.subject_analysis.length" class="report-section">
          <h4>科目分析</h4>
          <div v-for="s in dailyReport.subject_analysis" :key="s.subject" class="subject-row">
            <span>{{ s.subject }}</span>
            <el-progress :percentage="s.rate" :stroke-width="14" style="flex:1;margin:0 12px" />
            <span style="color:#909399;font-size:13px">{{ s.done }}/{{ s.total }}</span>
          </div>
        </div>
      </div>
      <div v-if="reportType === 'monthly' && monthlyReport" class="report-content">
        <div class="report-date">{{ monthlyReport.period }}</div>
        <div class="report-grid">
          <div class="report-metric">
            <div class="rm-value" style="color:#409eff">{{ monthlyReport.summary.tasks_completed }}</div>
            <div class="rm-label">完成任务</div>
          </div>
          <div class="report-metric">
            <div class="rm-value" style="color:#e6a23c">{{ monthlyReport.summary.pomodoro_minutes }}</div>
            <div class="rm-label">专注分钟</div>
          </div>
          <div class="report-metric">
            <div class="rm-value" style="color:#67c23a">{{ monthlyReport.summary.words_studied }}</div>
            <div class="rm-label">学习单词</div>
          </div>
          <div class="report-metric">
            <div class="rm-value" style="color:#f56c6c">{{ monthlyReport.summary.mastered_words }}/{{ monthlyReport.summary.total_words }}</div>
            <div class="rm-label">已掌握</div>
          </div>
        </div>
      </div>
    </el-dialog>
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
const showReport = ref(false);
const reportTitle = ref("");
const reportType = ref("daily");
const dailyReport = ref(null);
const monthlyReport = ref(null);

const goalLabel = (t) => ({ tasks: "完成任务", minutes: "学习时长", words: "学习单词" }[t] || t);

const statCards = computed(() => overview.value ? [
  { label: "总任务", value: overview.value.total_tasks, icon: "📋", color: "#409eff" },
  { label: "完成率", value: overview.value.completion_rate + "%", icon: "✅", color: "#67c23a" },
  { label: "今日学习", value: overview.value.today_study_minutes + "分钟", icon: "⏱️", color: "#e6a23c" },
  { label: "已掌握单词", value: `${overview.value.mastered_words}/${overview.value.total_words}`, icon: "📚", color: "#f56c6c" },
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

async function loadDailyReport() {
  try {
    const { data } = await exportApi.dailyReport(store.userId);
    dailyReport.value = data;
    reportType.value = "daily";
    reportTitle.value = "今日学习日报";
    showReport.value = true;
  } catch { ElMessage.error("加载日报失败"); }
}

async function loadMonthlyReport() {
  try {
    const { data } = await exportApi.monthlyReport(store.userId);
    monthlyReport.value = data;
    reportType.value = "monthly";
    reportTitle.value = "近30天学习月报";
    showReport.value = true;
  } catch { ElMessage.error("加载月报失败"); }
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

.stat-card { position: relative; overflow: hidden; }
.stat-card :deep(.el-card__body) { padding: 20px; }
.stat-icon { font-size: 28px; width: 48px; height: 48px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { color: var(--text-secondary); margin-top: 4px; font-size: 14px; }

/* 等高行 */
.chart-row { align-items: stretch; }
.chart-col { display: flex; }
.chart-card { flex: 1; display: flex; flex-direction: column; }
.chart-card :deep(.el-card__body) { flex: 1; display: flex; flex-direction: column; }

.chart-container { height: 250px; flex: 1; }
.habit-stat-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.hs-icon { font-size: 20px; }
.hs-name { width: 80px; }
.hs-count { color: #909399; font-size: 13px; }

.header-actions { display: flex; gap: 8px; }

.report-content { }
.report-date { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; }
.report-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.report-metric { text-align: center; padding: 12px; background: #fafafa; border-radius: var(--radius-sm); }
.rm-value { font-size: 28px; font-weight: 700; }
.rm-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.report-section { margin-top: 16px; }
.report-section h4 { font-size: 15px; margin-bottom: 12px; color: var(--text-primary); }
.goal-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.subject-row { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }

@media (max-width: 768px) {
  .stat-value { font-size: 22px; }
  .stat-icon { width: 40px; height: 40px; font-size: 22px; }
  .chart-container { height: 200px; }
  .report-grid { grid-template-columns: repeat(2, 1fr); }
  .rm-value { font-size: 22px; }
}
@media (max-width: 480px) {
  .report-grid { grid-template-columns: 1fr 1fr; }
}
</style>
