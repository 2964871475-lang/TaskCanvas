<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1 class="page-title">任务看板</h1>
      <div class="countdown" v-if="examDate">
        距离考研还有 <span class="days">{{ daysLeft }}</span> 天
      </div>
      <el-button type="primary" @click="showAdd = true">
        <el-icon><Plus /></el-icon> 新建任务
      </el-button>
    </div>

    <el-tabs v-model="activeCategory">
      <el-tab-pane label="每日任务" name="daily" />
      <el-tab-pane label="长期任务" name="longterm" />
      <el-tab-pane label="错题任务" name="mistake" />
    </el-tabs>

    <div class="task-columns">
      <div class="column" v-for="status in columns" :key="status.key">
        <h3>{{ status.label }}</h3>
        <div class="task-list">
          <el-card
            v-for="task in filteredTasks(status.key)"
            :key="task.id"
            shadow="hover"
            class="task-card"
          >
            <div class="task-title">{{ task.title }}</div>
            <div class="task-meta">
              <el-tag :type="priorityType(task.priority)" size="small">
                {{ priorityLabel(task.priority) }}
              </el-tag>
              <span class="subject">{{ task.subject }}</span>
            </div>
            <div class="task-actions">
              <el-button size="small" @click="moveTask(task, 'in_progress')" v-if="task.status === 'pending'">开始</el-button>
              <el-button size="small" type="success" @click="moveTask(task, 'done')" v-if="task.status !== 'done'">完成</el-button>
              <el-button size="small" @click="checkin(task)" v-if="task.status === 'done'">打卡</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAdd" title="新建任务">
      <el-form :model="newTask">
        <el-form-item label="标题"><el-input v-model="newTask.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="newTask.description" type="textarea" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="newTask.category">
            <el-option label="每日" value="daily" />
            <el-option label="长期" value="longterm" />
            <el-option label="错题" value="mistake" />
          </el-select>
        </el-form-item>
        <el-form-item label="科目">
          <el-select v-model="newTask.subject">
            <el-option label="数学" value="数学" />
            <el-option label="英语" value="英语" />
            <el-option label="政治" value="政治" />
            <el-option label="专业课" value="专业课" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="newTask.priority">
            <el-radio :value="1">高</el-radio>
            <el-radio :value="2">中</el-radio>
            <el-radio :value="3">低</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="createTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { taskApi } from "../api";

const examDate = new Date("2026-12-20");
const daysLeft = computed(() => Math.ceil((examDate - new Date()) / 86400000));

const activeCategory = ref("daily");
const tasks = ref([]);
const showAdd = ref(false);
const newTask = ref({
  title: "", description: "", category: "daily", subject: "数学", priority: 2, owner_id: 1,
});

const columns = [
  { key: "pending", label: "待办" },
  { key: "in_progress", label: "进行中" },
  { key: "done", label: "已完成" },
];

function filteredTasks(status) {
  return tasks.value.filter((t) => t.status === status && t.category === activeCategory.value);
}

function priorityType(p) {
  return p === 1 ? "danger" : p === 2 ? "warning" : "info";
}
function priorityLabel(p) {
  return p === 1 ? "高" : p === 2 ? "中" : "低";
}

async function loadTasks() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  if (!user.id) return;
  const { data } = await taskApi.list(user.id);
  tasks.value = data;
}

async function createTask() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  newTask.value.owner_id = user.id || 1;
  await taskApi.create(newTask.value);
  showAdd.value = false;
  loadTasks();
}

async function moveTask(task, status) {
  await taskApi.update(task.id, { status });
  loadTasks();
}

async function checkin(task) {
  await taskApi.checkin(task.id);
  ElMessage.success(`连续打卡 ${task.streak_days + 1} 天`);
  loadTasks();
}

onMounted(loadTasks);
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.countdown {
  font-size: 16px;
  color: #606266;
}
.countdown .days {
  font-size: 28px;
  font-weight: 700;
  color: #e6a23c;
}
.task-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.column h3 {
  margin-bottom: 12px;
  color: #909399;
}
.task-card {
  margin-bottom: 8px;
}
.task-title {
  font-weight: 600;
  margin-bottom: 8px;
}
.task-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #909399;
}
.task-actions {
  display: flex;
  gap: 4px;
}
</style>
