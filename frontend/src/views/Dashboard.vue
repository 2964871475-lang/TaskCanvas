<template>
  <div class="dashboard-page">
    <h1 class="page-title">数据可视化驾驶舱</h1>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="6" v-for="s in statCards" :key="s.label">
        <el-card shadow="hover">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header>近7天任务完成趋势</template>
          <div class="chart-container">
            <Line v-if="taskChartData" :data="taskChartData" :options="chartOptions" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>近7天单词学习趋势</template>
          <div class="chart-container">
            <Line v-if="wordChartData" :data="wordChartData" :options="chartOptions" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header>单词掌握度分布</template>
          <div class="chart-container">
            <Bar v-if="masteryData" :data="masteryData" :options="chartOptions" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>学习概览</template>
          <div class="chart-container">
            <Doughnut v-if="overviewPieData" :data="overviewPieData" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { Line, Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Title, Tooltip, Legend, Filler,
} from "chart.js";
import { statsApi } from "../api";

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Title, Tooltip, Legend, Filler
);

const overview = ref(null);
const weeklyTasks = ref([]);
const weeklyWords = ref([]);
const masteryHeatmap = ref([]);

const chartOptions = { responsive: true, maintainAspectRatio: false };

function getUser() {
  return JSON.parse(localStorage.getItem("user") || "{}");
}

const statCards = computed(() => {
  if (!overview.value) return [];
  return [
    { label: "总任务", value: overview.value.total_tasks },
    { label: "完成率", value: overview.value.completion_rate + "%" },
    { label: "今日学习", value: overview.value.today_study_minutes + "分钟" },
    { label: "已掌握单词", value: overview.value.mastered_words + "/" + overview.value.total_words },
  ];
});

const taskChartData = computed(() => {
  if (!weeklyTasks.value.length) return null;
  return {
    labels: weeklyTasks.value.map((d) => d.date),
    datasets: [{ label: "完成任务数", data: weeklyTasks.value.map((d) => d.count), borderColor: "#409eff", backgroundColor: "rgba(64,158,255,0.1)", fill: true, tension: 0.3 }],
  };
});

const wordChartData = computed(() => {
  if (!weeklyWords.value.length) return null;
  return {
    labels: weeklyWords.value.map((d) => d.date),
    datasets: [{ label: "学习单词数", data: weeklyWords.value.map((d) => d.count), borderColor: "#67c23a", backgroundColor: "rgba(103,194,58,0.1)", fill: true, tension: 0.3 }],
  };
});

const masteryData = computed(() => {
  if (!masteryHeatmap.value.length) return null;
  return {
    labels: masteryHeatmap.value.map((d) => d.range),
    datasets: [{ label: "单词数", data: masteryHeatmap.value.map((d) => d.count), backgroundColor: ["#f56c6c", "#e6a23c", "#409eff", "#67c23a", "#00b894"] }],
  };
});

const overviewPieData = computed(() => {
  if (!overview.value) return null;
  return {
    labels: ["已完成", "进行中", "待办"],
    datasets: [{ data: [overview.value.done, overview.value.in_progress, overview.value.pending], backgroundColor: ["#67c23a", "#409eff", "#909399"] }],
  };
});

onMounted(async () => {
  const user = getUser();
  if (!user.id) return;
  const [ov, wt, wm, mh] = await Promise.all([
    statsApi.overview(user.id),
    statsApi.weeklyTasks(user.id),
    statsApi.weeklyWords(user.id),
    statsApi.masteryHeatmap(user.id),
  ]);
  overview.value = ov.data;
  weeklyTasks.value = wt.data;
  weeklyWords.value = wm.data;
  masteryHeatmap.value = mh.data;
});
</script>

<style scoped>
.stat-cards .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}
.stat-label {
  color: #909399;
  margin-top: 4px;
}
.chart-container {
  height: 250px;
}
</style>
