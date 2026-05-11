<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1 class="page-title">任务看板</h1>
      <div class="countdown" v-if="examDate">
        距离考研还有 <span class="days">{{ daysLeft }}</span> 天
      </div>
      <div class="header-actions">
        <el-select v-model="filterSubject" placeholder="科目筛选" clearable size="small" style="width:100px">
          <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
        </el-select>
        <el-select v-model="filterPriority" placeholder="优先级" clearable size="small" style="width:100px">
          <el-option label="高" :value="1" /><el-option label="中" :value="2" /><el-option label="低" :value="3" />
        </el-select>
        <el-button type="primary" @click="openAdd"><el-icon><Plus /></el-icon> 新建任务</el-button>
      </div>
    </div>

    <el-tabs v-model="activeCategory">
      <el-tab-pane label="每日任务" name="daily" />
      <el-tab-pane label="长期任务" name="longterm" />
      <el-tab-pane label="错题任务" name="mistake" />
    </el-tabs>

    <div class="task-columns">
      <div class="column" v-for="col in columns" :key="col.key">
        <h3>{{ col.label }}</h3>
        <draggable :list="filteredTasks(col.key)" item-key="id" group="tasks" @end="onDragEnd" ghost-class="ghost">
          <template #item="{ element }">
            <el-card shadow="hover" class="task-card" @click="openDetail(element)">
              <div class="task-title">{{ element.title }}</div>
              <div class="task-meta">
                <el-tag :type="priorityType(element.priority)" size="small">{{ priorityLabel(element.priority) }}</el-tag>
                <span class="subject">{{ element.subject }}</span>
                <span v-if="element.streak_days" class="streak">🔥{{ element.streak_days }}天</span>
              </div>
              <div v-if="element.deadline" class="task-deadline">
                <el-icon><Clock /></el-icon> {{ formatDate(element.deadline) }}
              </div>
              <div class="task-actions">
                <el-button size="small" @click.stop="moveTask(element, 'in_progress')" v-if="element.status === 'pending'">开始</el-button>
                <el-button size="small" type="success" @click.stop="moveTask(element, 'done')" v-if="element.status !== 'done'">完成</el-button>
                <el-button size="small" @click.stop="checkinTask(element)" v-if="element.status === 'done'">打卡</el-button>
                <el-button size="small" type="danger" text @click.stop="deleteTask(element)">删除</el-button>
              </div>
            </el-card>
          </template>
        </draggable>
      </div>
    </div>

    <!-- 新建/编辑任务对话框 -->
    <el-dialog v-model="showDialog" :title="editingTask ? '编辑任务' : '新建任务'">
      <el-form :model="taskForm">
        <el-form-item label="标题"><el-input v-model="taskForm.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="taskForm.description" type="textarea" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="taskForm.category">
                <el-option label="每日" value="daily" /><el-option label="长期" value="longterm" /><el-option label="错题" value="mistake" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="科目">
              <el-select v-model="taskForm.subject">
                <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-radio-group v-model="taskForm.priority">
                <el-radio :value="1">高</el-radio><el-radio :value="2">中</el-radio><el-radio :value="3">低</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止时间"><el-date-picker v-model="taskForm.deadline" type="datetime" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="预计时长(分钟)"><el-input-number v-model="taskForm.estimated_minutes" :min="5" :max="480" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">{{ editingTask ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情/评论 -->
    <el-dialog v-model="showDetail" title="任务详情" width="500px">
      <div v-if="detailTask">
        <h3>{{ detailTask.title }}</h3>
        <p style="color:#909399;margin:8px 0">{{ detailTask.description || '暂无描述' }}</p>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="分类">{{ detailTask.category }}</el-descriptions-item>
          <el-descriptions-item label="科目">{{ detailTask.subject }}</el-descriptions-item>
          <el-descriptions-item label="优先级">{{ priorityLabel(detailTask.priority) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detailTask.status }}</el-descriptions-item>
          <el-descriptions-item label="连续打卡">{{ detailTask.streak_days }}天</el-descriptions-item>
          <el-descriptions-item label="预计时长">{{ detailTask.estimated_minutes }}分钟</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <h4>评论</h4>
        <CommentSection :task-id="detailTask.id" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import draggable from "vuedraggable";
import dayjs from "dayjs";
import { taskApi } from "../api";
import { useUserStore } from "../stores/user";
import CommentSection from "../components/CommentSection.vue";

const store = useUserStore();
const examDate = new Date("2026-12-20");
const daysLeft = computed(() => Math.ceil((examDate - new Date()) / 86400000));
const subjects = ["数学", "英语", "政治", "专业课", "其他"];

const activeCategory = ref("daily");
const tasks = ref([]);
const filterSubject = ref("");
const filterPriority = ref(null);
const showDialog = ref(false);
const showDetail = ref(false);
const editingTask = ref(null);
const detailTask = ref(null);
const taskForm = ref({ title: "", description: "", category: "daily", subject: "数学", priority: 2, estimated_minutes: 60, deadline: null });

const columns = [
  { key: "pending", label: "待办" },
  { key: "in_progress", label: "进行中" },
  { key: "done", label: "已完成" },
];

function filteredTasks(status) {
  return tasks.value.filter((t) => {
    if (t.status !== status || t.category !== activeCategory.value) return false;
    if (filterSubject.value && t.subject !== filterSubject.value) return false;
    if (filterPriority.value && t.priority !== filterPriority.value) return false;
    return true;
  });
}

function priorityType(p) { return p === 1 ? "danger" : p === 2 ? "warning" : "info"; }
function priorityLabel(p) { return p === 1 ? "高" : p === 2 ? "中" : "低"; }
function formatDate(d) { return dayjs(d).format("MM-DD HH:mm"); }

async function loadTasks() {
  if (!store.userId) return;
  const { data } = await taskApi.list(store.userId);
  tasks.value = data;
}

function openAdd() {
  editingTask.value = null;
  taskForm.value = { title: "", description: "", category: activeCategory.value, subject: "数学", priority: 2, estimated_minutes: 60, deadline: null };
  showDialog.value = true;
}

function openDetail(task) {
  detailTask.value = task;
  showDetail.value = true;
}

async function saveTask() {
  if (editingTask.value) {
    await taskApi.update(editingTask.value.id, taskForm.value);
  } else {
    await taskApi.create({ ...taskForm.value, owner_id: store.userId });
  }
  showDialog.value = false;
  loadTasks();
}

async function moveTask(task, status) {
  await taskApi.update(task.id, { status });
  loadTasks();
}

async function checkinTask(task) {
  const { data } = await taskApi.checkin(task.id);
  ElMessage.success(`连续打卡 ${data.streak_days} 天`);
  loadTasks();
}

async function deleteTask(task) {
  await ElMessageBox.confirm("确定删除该任务？", "提示", { type: "warning" });
  await taskApi.delete(task.id);
  loadTasks();
}

async function onDragEnd() {
  const items = [];
  columns.forEach((col) => {
    filteredTasks(col.key).forEach((t, i) => {
      items.push({ id: t.id, sort_order: i });
    });
  });
  if (items.length) await taskApi.batchSort(items);
}

onMounted(loadTasks);
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.countdown { font-size: 16px; color: #606266; }
.countdown .days { font-size: 28px; font-weight: 700; color: #e6a23c; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.task-columns { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.column h3 { margin-bottom: 12px; color: #909399; }
.task-card { margin-bottom: 8px; cursor: pointer; }
.task-title { font-weight: 600; margin-bottom: 8px; }
.task-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 4px; font-size: 13px; color: #909399; }
.task-deadline { font-size: 12px; color: #e6a23c; margin-bottom: 8px; display: flex; align-items: center; gap: 4px; }
.streak { color: #e6a23c; font-weight: 600; }
.task-actions { display: flex; gap: 4px; flex-wrap: wrap; }
.ghost { opacity: 0.4; background: #ecf5ff; border: 2px dashed #409eff; }
</style>
