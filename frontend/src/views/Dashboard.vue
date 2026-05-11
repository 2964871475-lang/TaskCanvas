<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title">
        <span class="page-title-icon">📊</span>
        数据可视化驾驶舱
      </h1>
      <el-button type="primary" @click="exportReport">
        <el-icon><Download /></el-icon>
        导出周报
      </el-button>
    </div>

    <!-- Stat cards -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="s in statCards" :key="s.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon">{{ s.icon }}</div>
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>近7天任务完成趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <Line v-if="taskChartData" :data="taskChartData" :options="chartOpts" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>近7天单词学习趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <Line v-if="wordChartData" :data="wordChartData" :options="chartOpts" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>近7天番茄钟专注时长</span>
            </div>
          </template>
          <div class="chart-container">
            <Bar v-if="pomodoroData" :data="pomodoroData" :options="chartOpts" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>单词掌握度分布</span>
            </div>
          </template>
          <div class="chart-container">
            <Doughnut v-if="masteryData" :data="masteryData" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>学习活跃度热力图</span>
            </div>
          </template>
          <HeatMap :data="heatmapData" :weeks="12" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>习惯打卡统计</span>
            </div>
          </template>
          <div class="habit-list">
            <div v-for="h in habitStats" :key="h.habit_id" class="habit-item">
              <div class="habit-info">
                <span class="habit-icon">{{ h.icon }}</span>
                <span class="habit-name">{{ h.name }}</span>
              </div>
              <div class="habit-progress">
                <el-progress
                  :percentage="Math.min(100, Math.round(h.total_records / 30 * 100))"
                  :stroke-width="8"
                />
              </div>
              <span class="habit-count">{{ h.total_records }}次</span>
            </div>
            <el-empty v-if="!habitStats.length" description="暂无习惯数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row v-if="teamComparison.length" :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>小组成员学习对比（本周）</span>
            </div>
          </template>
          <div class="chart-container team-chart">
            <Bar :data="teamChartData" :options="chartOpts" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Line, Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from "chart.js";
import { Download } from "@element-plus/icons-vue";
import { statsApi, exportApi } from "../api";
import { useUserStore } from "../stores/user";
import HeatMap from "../components/HeatMap.vue";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const store = useUserStore();
const overview = ref(null);
const weeklyTasks = ref([]);
const weeklyWords = ref([]);
const weeklyPomodoro = ref([]);
const masteryHeatmap = ref([]);
const habitStats = ref([]);
const teamComparison = ref([]);
const heatmapData = ref([]);

const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#606266',
        font: {
          family: 'Noto Sans SC'
        }
      }
    }
  },
  scales: {
    x: {
      ticks: { color: '#909399' },
      grid: { color: 'rgba(0, 0, 0, 0.04)' }
    },
    y: {
      ticks: { color: '#909399' },
      grid: { color: 'rgba(0, 0, 0, 0.04)' }
    }
  }
};

const statCards = computed(() =>
  overview.value
    ? [
        { label: "总任务", value: overview.value.total_tasks, icon: "📋" },
        { label: "完成率", value: overview.value.completion_rate + "%", icon: "✅" },
        { label: "今日学习", value: overview.value.today_study_minutes + "分钟", icon: "📚" },
        { label: "已掌握单词", value: `${overview.value.mastered_words}/${overview.value.total_words}`, icon: "🎯" }
      ]
    : []
);

const taskChartData = computed(() =>
  weeklyTasks.value.length
    ? {
        labels: weeklyTasks.value.map((d) => d.date),
        datasets: [{
          label: "完成任务数",
          data: weeklyTasks.value.map((d) => d.count),
          borderColor: "#4A90D9",
          backgroundColor: "rgba(74, 144, 217, 0.1)",
          fill: true,
          tension: 0.3,
          pointBackgroundColor: "#4A90D9",
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      }
    : null
);

const wordChartData = computed(() =>
  weeklyWords.value.length
    ? {
        labels: weeklyWords.value.map((d) => d.date),
        datasets: [{
          label: "学习单词数",
          data: weeklyWords.value.map((d) => d.count),
          borderColor: "#67C23A",
          backgroundColor: "rgba(103, 194, 58, 0.1)",
          fill: true,
          tension: 0.3,
          pointBackgroundColor: "#67C23A",
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      }
    : null
);

const pomodoroData = computed(() =>
  weeklyPomodoro.value.length
    ? {
        labels: weeklyPomodoro.value.map((d) => d.date),
        datasets: [{
          label: "专注时长(分钟)",
          data: weeklyPomodoro.value.map((d) => d.minutes),
          backgroundColor: "rgba(230, 162, 60, 0.8)",
          borderColor: "#E6A23C",
          borderWidth: 1,
          borderRadius: 4
        }]
      }
    : null
);

const masteryData = computed(() =>
  masteryHeatmap.value.length
    ? {
        labels: masteryHeatmap.value.map((d) => d.range),
        datasets: [{
          data: masteryHeatmap.value.map((d) => d.count),
          backgroundColor: [
            "rgba(245, 108, 108, 0.8)",
            "rgba(230, 162, 60, 0.8)",
            "rgba(74, 144, 217, 0.8)",
            "rgba(103, 194, 58, 0.8)",
            "rgba(64, 158, 255, 0.8)"
          ]
        }]
      }
    : null
);

const teamChartData = computed(() =>
  teamComparison.value.length
    ? {
        labels: teamComparison.value.map((d) => d.username),
        datasets: [
          { label: "完成任务", data: teamComparison.value.map((d) => d.tasks_done), backgroundColor: "rgba(74, 144, 217, 0.8)" },
          { label: "学习单词", data: teamComparison.value.map((d) => d.words_learned), backgroundColor: "rgba(103, 194, 58, 0.8)" },
          { label: "番茄钟(分钟)", data: teamComparison.value.map((d) => d.pomodoro_minutes), backgroundColor: "rgba(230, 162, 60, 0.8)" }
        ]
      }
    : null
);

async function exportReport() {
  try {
    const res = await exportApi.weeklyReport(store.userId);
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "weekly_report.png";
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("周报已下载");
  } catch {
    ElMessage.error("导出失败");
  }
}

onMounted(async () => {
  if (!store.userId) return;
  const [ov, wt, wm, wp, mh, hs] = await Promise.all([
    statsApi.overview(store.userId),
    statsApi.weeklyTasks(store.userId),
    statsApi.weeklyWords(store.userId),
    statsApi.weeklyPomodoro(store.userId),
    statsApi.masteryHeatmap(store.userId),
    statsApi.habitStreak(store.userId)
  ]);
  overview.value = ov.data;
  weeklyTasks.value = wt.data;
  weeklyWords.value = wm.data;
  weeklyPomodoro.value = wp.data;
  masteryHeatmap.value = mh.data;
  habitStats.value = hs.data;

  const merged = {};
  wt.data.forEach((d) => { merged[d.date] = (merged[d.date] || 0) + d.count; });
  wm.data.forEach((d) => { merged[d.date] = (merged[d.date] || 0) + d.count; });
  heatmapData.value = Object.entries(merged).map(([date, count]) => ({ date, count }));

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
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 8px 0;
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.charts-row {
  margin-bottom: 20px;
}

.chart-header {
  font-weight: 600;
  color: var(--text-primary);
}

.chart-container {
  height: 280px;
}

.team-chart {
  height: 320px;
}

/* Habit list */
.habit-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.habit-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
  transition: background 0.2s ease;
}

.habit-item:hover {
  background: #E8F0FE;
}

.habit-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

.habit-icon {
  font-size: 22px;
}

.habit-name {
  font-weight: 500;
  color: var(--text-primary);
}

.habit-progress {
  flex: 1;
}

.habit-count {
  color: var(--text-secondary);
  font-size: 14px;
  min-width: 50px;
  text-align: right;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .stat-cards .el-col {
    margin-bottom: 12px;
  }

  .charts-row .el-col {
    margin-bottom: 12px;
  }
}
</style>
