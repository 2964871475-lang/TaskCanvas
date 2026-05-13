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
        <el-button @click="exportTasks" size="small"><el-icon><Download /></el-icon> 导出</el-button>
        <el-button @click="triggerImport" size="small"><el-icon><Upload /></el-icon> 导入</el-button>
        <input ref="fileInput" type="file" accept=".json" style="display:none" @change="importTasks" />
        <el-button :type="batchMode ? 'warning' : 'default'" @click="toggleBatchMode" size="small">
          {{ batchMode ? '退出批量' : '批量管理' }}
        </el-button>
        <el-button type="primary" @click="openAdd" :disabled="batchMode"><el-icon><Plus /></el-icon> 新建任务</el-button>
      </div>
    </div>

    <el-tabs v-model="activeCategory">
      <el-tab-pane label="每日任务" name="daily" />
      <el-tab-pane label="长期任务" name="longterm" />
      <el-tab-pane label="错题任务" name="mistake" />
    </el-tabs>

    <div class="task-columns">
      <!-- 待办列（带日期导航） -->
      <div class="column column-pending">
        <div class="column-header">
          <h3>待办</h3>
          <el-badge :value="filteredTasks('pending').length" :max="99" type="primary" />
        </div>
        <div class="date-nav">
          <el-date-picker v-model="selectedDate" type="date" size="small" format="MM/DD (ddd)" value-format="YYYY-MM-DD" :clearable="false" style="width: 150px" />
          <el-button v-if="!isToday" text size="small" type="primary" @click="goToday">回到今天</el-button>
        </div>
        <draggable :list="filteredTasks('pending')" item-key="id" group="tasks" @end="onDragEnd" ghost-class="ghost" :disabled="batchMode">
          <template #item="{ element }">
            <el-card shadow="hover" class="task-card" :class="{ selected: selectedIds.has(element.id) }" @click="handleCardClick(element)">
              <div class="task-title">
                <el-checkbox v-if="batchMode" :model-value="selectedIds.has(element.id)" @click.stop @change="toggleSelect(element)" class="task-checkbox" />
                {{ element.title }}
              </div>
              <div class="task-meta">
                <el-tag :type="priorityType(element.priority)" size="small">{{ priorityLabel(element.priority) }}</el-tag>
                <span class="subject">{{ element.subject }}</span>
              </div>
              <div v-if="element.deadline" class="task-deadline">
                <el-icon><Clock /></el-icon> {{ formatDate(element.deadline) }}
              </div>
              <div class="task-actions" v-if="!batchMode">
                <el-button size="small" @click.stop="moveTask(element, 'in_progress')">开始</el-button>
                <el-button size="small" type="success" @click.stop="moveTask(element, 'done')">完成</el-button>
                <el-button size="small" type="danger" text @click.stop="deleteTask(element)">删除</el-button>
              </div>
            </el-card>
          </template>
        </draggable>
        <el-empty v-if="!filteredTasks('pending').length" description="当天暂无待办任务" :image-size="60" />
      </div>

      <!-- 进行列 -->
      <div class="column column-in_progress">
        <div class="column-header">
          <h3>进行中</h3>
          <el-badge :value="filteredTasks('in_progress').length" :max="99" type="warning" />
        </div>
        <draggable :list="filteredTasks('in_progress')" item-key="id" group="tasks" @end="onDragEnd" ghost-class="ghost" :disabled="batchMode">
          <template #item="{ element }">
            <el-card shadow="hover" class="task-card" :class="{ selected: selectedIds.has(element.id) }" @click="handleCardClick(element)">
              <div class="task-title">
                <el-checkbox v-if="batchMode" :model-value="selectedIds.has(element.id)" @click.stop @change="toggleSelect(element)" class="task-checkbox" />
                {{ element.title }}
              </div>
              <div class="task-meta">
                <el-tag :type="priorityType(element.priority)" size="small">{{ priorityLabel(element.priority) }}</el-tag>
                <span class="subject">{{ element.subject }}</span>
                <span v-if="element.streak_days" class="streak">🔥{{ element.streak_days }}天</span>
              </div>
              <div v-if="element.deadline" class="task-deadline">
                <el-icon><Clock /></el-icon> {{ formatDate(element.deadline) }}
              </div>
              <div class="task-actions" v-if="!batchMode">
                <el-button size="small" @click.stop="moveTask(element, 'done')" type="success">完成</el-button>
                <el-button size="small" type="danger" text @click.stop="deleteTask(element)">删除</el-button>
              </div>
            </el-card>
          </template>
        </draggable>
      </div>

      <!-- 已完成列 -->
      <div class="column column-done">
        <div class="column-header">
          <h3>已完成</h3>
          <el-badge :value="filteredTasks('done').length" :max="99" type="success" />
        </div>
        <draggable :list="filteredTasks('done')" item-key="id" group="tasks" @end="onDragEnd" ghost-class="ghost" :disabled="batchMode">
          <template #item="{ element }">
            <el-card shadow="hover" class="task-card" :class="{ selected: selectedIds.has(element.id) }" @click="handleCardClick(element)">
              <div class="task-title">
                <el-checkbox v-if="batchMode" :model-value="selectedIds.has(element.id)" @click.stop @change="toggleSelect(element)" class="task-checkbox" />
                {{ element.title }}
              </div>
              <div class="task-meta">
                <el-tag :type="priorityType(element.priority)" size="small">{{ priorityLabel(element.priority) }}</el-tag>
                <span class="subject">{{ element.subject }}</span>
                <span v-if="element.streak_days" class="streak">🔥{{ element.streak_days }}天</span>
              </div>
              <div class="task-actions" v-if="!batchMode">
                <el-button size="small" @click.stop="checkinTask(element)">打卡</el-button>
                <el-button size="small" type="danger" text @click.stop="deleteTask(element)">删除</el-button>
              </div>
            </el-card>
          </template>
        </draggable>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <transition name="page-fade">
      <div v-if="batchMode" class="batch-bar">
        <div class="batch-info">
          <el-checkbox :model-value="isAllSelected" :indeterminate="isIndeterminate" @change="toggleSelectAll">全选</el-checkbox>
          <span class="batch-count">已选 {{ selectedIds.size }} 条</span>
        </div>
        <div class="batch-actions">
          <el-button type="danger" :disabled="!selectedIds.size" @click="batchDelete">
            <el-icon><Delete /></el-icon> 删除选中
          </el-button>
          <el-button @click="toggleBatchMode">取消</el-button>
        </div>
      </div>
    </transition>

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
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划日期"><el-date-picker v-model="taskForm.scheduled_date" type="date" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计时长(分钟)"><el-input-number v-model="taskForm.estimated_minutes" :min="5" :max="480" /></el-form-item>
          </el-col>
        </el-row>
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
          <el-descriptions-item label="计划日期">{{ detailTask.scheduled_date ? dayjs(detailTask.scheduled_date).format("YYYY-MM-DD") : "未设置" }}</el-descriptions-item>
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
const fileInput = ref(null);

const activeCategory = ref("daily");
const tasks = ref([]);
const filterSubject = ref("");
const filterPriority = ref(null);
const showDialog = ref(false);
const showDetail = ref(false);
const editingTask = ref(null);
const detailTask = ref(null);
const selectedDate = ref(dayjs().format("YYYY-MM-DD"));

const batchMode = ref(false);
const selectedIds = ref(new Set());

const taskForm = ref({
  title: "", description: "", category: "daily", subject: "数学",
  priority: 2, estimated_minutes: 60, deadline: null, scheduled_date: new Date(),
});

const isToday = computed(() => selectedDate.value === dayjs().format("YYYY-MM-DD"));

const allVisibleTasks = computed(() => {
  return ["pending", "in_progress", "done"].flatMap((s) => filteredTasks(s));
});

const isAllSelected = computed(() => {
  const visible = allVisibleTasks.value;
  return visible.length > 0 && visible.every((t) => selectedIds.value.has(t.id));
});

const isIndeterminate = computed(() => {
  const visible = allVisibleTasks.value;
  const selected = visible.filter((t) => selectedIds.value.has(t.id)).length;
  return selected > 0 && selected < visible.length;
});

function goToday() {
  selectedDate.value = dayjs().format("YYYY-MM-DD");
}

function toggleBatchMode() {
  batchMode.value = !batchMode.value;
  if (!batchMode.value) selectedIds.value.clear();
}

function toggleSelect(task) {
  const s = new Set(selectedIds.value);
  if (s.has(task.id)) s.delete(task.id);
  else s.add(task.id);
  selectedIds.value = s;
}

function toggleSelectAll(val) {
  if (val) {
    selectedIds.value = new Set(allVisibleTasks.value.map((t) => t.id));
  } else {
    selectedIds.value.clear();
  }
}

function handleCardClick(task) {
  if (batchMode.value) {
    toggleSelect(task);
  } else {
    openDetail(task);
  }
}

function filteredTasks(status) {
  return tasks.value.filter((t) => {
    if (t.status !== status || t.category !== activeCategory.value) return false;
    if (filterSubject.value && t.subject !== filterSubject.value) return false;
    if (filterPriority.value && t.priority !== filterPriority.value) return false;
    if (status === "pending") {
      const taskDate = t.scheduled_date ? dayjs(t.scheduled_date).format("YYYY-MM-DD") : null;
      if (taskDate !== selectedDate.value) return false;
    }
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
  taskForm.value = {
    title: "", description: "", category: activeCategory.value, subject: "数学",
    priority: 2, estimated_minutes: 60, deadline: null, scheduled_date: selectedDate.value + "T00:00:00",
  };
  showDialog.value = true;
}

function openDetail(task) {
  detailTask.value = task;
  showDetail.value = true;
}

async function saveTask() {
  if (!taskForm.value.title.trim()) { ElMessage.warning("请输入任务标题"); return; }
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

async function batchDelete() {
  if (!selectedIds.value.size) return;
  await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.size} 条任务？`, "批量删除", { type: "warning" });
  await taskApi.batchDelete([...selectedIds.value]);
  ElMessage.success(`已删除 ${selectedIds.value.size} 条任务`);
  selectedIds.value.clear();
  loadTasks();
}

async function onDragEnd() {
  const items = [];
  ["pending", "in_progress", "done"].forEach((status) => {
    filteredTasks(status).forEach((t, i) => {
      items.push({ id: t.id, sort_order: i });
    });
  });
  if (items.length) await taskApi.batchSort(items);
}

async function exportTasks() {
  try {
    const { data } = await taskApi.export(store.userId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tasks_${dayjs().format("YYYY-MM-DD")}.json`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success(`已导出 ${data.count} 条任务`);
  } catch {
    ElMessage.error("导出失败");
  }
}

function triggerImport() {
  fileInput.value?.click();
}

async function importTasks(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  try {
    const { data } = await taskApi.import(store.userId, formData);
    ElMessage.success(data.message);
    loadTasks();
  } catch {
    ElMessage.error("导入失败");
  } finally {
    if (fileInput.value) fileInput.value.value = "";
  }
}

onMounted(loadTasks);
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.countdown { font-size: 16px; color: #606266; }
.countdown .days { font-size: 28px; font-weight: 700; color: #e6a23c; }
.header-actions { display: flex; gap: 8px; align-items: center; }

.task-columns { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.column {
  border-radius: var(--radius-md);
  padding: 16px;
  min-height: 300px;
  transition: background var(--transition-fast);
}
.column-pending { background: #fafafa; border: 1px solid #ebeef5; }
.column-in_progress { background: #fdf6ec; border: 1px solid #faecd8; }
.column-done { background: #f0f9eb; border: 1px solid #e1f3d8; }

.column-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.column-header h3 { color: var(--text-regular); font-size: 15px; }

.date-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 6px 8px;
  background: rgba(64, 158, 255, 0.06);
  border-radius: var(--radius-sm);
}

.task-card { margin-bottom: 8px; cursor: pointer; border-radius: var(--radius-sm); transition: border-color var(--transition-fast); }
.task-card.selected { border-color: var(--primary); background: var(--primary-bg); }
.task-title { font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.task-checkbox { flex-shrink: 0; }
.task-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 4px; font-size: 13px; color: #909399; }
.task-deadline { font-size: 12px; color: #e6a23c; margin-bottom: 8px; display: flex; align-items: center; gap: 4px; }
.streak { color: #e6a23c; font-weight: 600; }
.task-actions { display: flex; gap: 4px; flex-wrap: wrap; }
.ghost { opacity: 0.4; background: #ecf5ff; border: 2px dashed #409eff; border-radius: var(--radius-sm); }

/* 批量操作栏 */
.batch-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #fff;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.1);
}
.batch-info { display: flex; align-items: center; gap: 16px; }
.batch-count { font-size: 14px; color: var(--text-secondary); }
.batch-actions { display: flex; gap: 8px; }

@media (max-width: 768px) {
  .task-columns { grid-template-columns: 1fr; }
  .header-actions { flex-wrap: wrap; }
  .header-actions .el-select { width: 80px !important; }
  .column { min-height: auto; padding: 12px; }
  .date-nav { flex-wrap: wrap; }
  .batch-bar { flex-direction: column; gap: 8px; padding: 10px 16px; }
}
@media (max-width: 480px) {
  .countdown .days { font-size: 22px; }
  .task-actions { gap: 2px; }
  .task-actions .el-button { padding: 4px 8px; font-size: 12px; }
}
</style>
