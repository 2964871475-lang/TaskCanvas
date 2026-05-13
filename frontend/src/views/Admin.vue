<template>
  <div class="admin-page">
    <div class="page-header">
      <h1 class="page-title">管理后台</h1>
      <el-tag type="danger" size="small">系统管理员</el-tag>
    </div>

    <el-tabs v-model="activeTab" class="admin-tabs">
      <!-- ==================== Tab1: 系统概览 ==================== -->
      <el-tab-pane label="系统概览" name="overview">
        <div class="stats-grid">
          <div class="stat-card" v-for="s in statCards" :key="s.label">
            <div class="stat-icon" :style="{ background: s.color }">
              <el-icon :size="24"><component :is="s.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ s.value }}</div>
              <div class="stat-label">{{ s.label }}</div>
            </div>
          </div>
        </div>
        <div class="export-section">
          <el-button type="primary" size="large" @click="exportData">
            <el-icon><Download /></el-icon> 导出全量数据
          </el-button>
          <span class="export-tip">导出所有用户、任务、团队、学习数据为JSON</span>
        </div>
      </el-tab-pane>

      <!-- ==================== Tab2: 用户管理 ==================== -->
      <el-tab-pane label="用户管理" name="users">
        <div class="tab-toolbar">
          <el-input v-model="userSearch" placeholder="搜索用户名/邮箱" clearable size="default" style="width:260px" />
        </div>
        <el-table :data="filteredUsers" stripe style="width:100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" width="140" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="task_count" label="任务数" width="80" align="center" />
          <el-table-column label="角色" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">{{ row.is_admin ? '管理员' : '普通用户' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_disabled ? 'danger' : 'success'" size="small">{{ row.is_disabled ? '已禁用' : '正常' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" width="110">
            <template #default="{ row }">{{ fmtDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="220" align="center">
            <template #default="{ row }">
              <template v-if="!row.is_admin">
                <el-button size="small" :type="row.is_disabled ? 'success' : 'warning'" @click="toggleDisable(row)">{{ row.is_disabled ? '启用' : '禁用' }}</el-button>
                <el-button size="small" type="primary" @click="resetPwd(row)">重置密码</el-button>
                <el-button size="small" type="danger" text @click="deleteUser(row)">删除</el-button>
              </template>
              <span v-else style="color:#909399;font-size:12px">—</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ==================== Tab3: 团队审核 ==================== -->
      <el-tab-pane label="团队审核" name="teams">
        <el-table :data="teams" stripe style="width:100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="团队名称" width="160" />
          <el-table-column prop="owner_name" label="组长" width="100" />
          <el-table-column prop="member_count" label="成员数" width="80" align="center" />
          <el-table-column prop="invite_code" label="邀请码" width="140" />
          <el-table-column label="创建时间" width="110">
            <template #default="{ row }">{{ fmtDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="280" align="center">
            <template #default="{ row }">
              <el-button size="small" @click="viewTeamMembers(row)">成员</el-button>
              <el-button size="small" type="primary" @click="viewTeamStats(row)">统计</el-button>
              <el-button size="small" type="warning" @click="openTransfer(row)">转组长</el-button>
              <el-button size="small" type="success" @click="openAnnounce(row)">发布公告</el-button>
              <el-button size="small" type="danger" text @click="dissolveTeam(row)">解散</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 公告列表 -->
        <div class="section-title">
          <span>公告管理</span>
          <el-button size="small" type="primary" @click="openAnnounce(null)">发布全局公告</el-button>
        </div>
        <el-table :data="announcements" stripe style="width:100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" width="200" />
          <el-table-column prop="content" label="内容" show-overflow-tooltip />
          <el-table-column label="范围" width="120">
            <template #default="{ row }">
              <el-tag :type="row.team_id ? 'info' : 'danger'" size="small">{{ row.team_id ? row.team_name : '全局' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="publisher_name" label="发布者" width="100" />
          <el-table-column label="时间" width="110">
            <template #default="{ row }">{{ fmtDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-button size="small" type="danger" text @click="deleteAnnounce(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ==================== Tab4: 操作日志 ==================== -->
      <el-tab-pane label="操作日志" name="logs">
        <el-table :data="logs" stripe style="width:100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="operator_name" label="操作人" width="100" />
          <el-table-column label="操作类型" width="140">
            <template #default="{ row }">
              <el-tag :type="actionTagType(row.action)" size="small">{{ actionLabel(row.action) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="target_type" label="目标类型" width="90" />
          <el-table-column prop="target_id" label="目标ID" width="80" />
          <el-table-column prop="detail" label="详情" show-overflow-tooltip />
          <el-table-column label="时间" width="160">
            <template #default="{ row }">{{ fmtDateTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="logPage"
            :page-size="logSize"
            :total="logTotal"
            layout="total, prev, pager, next"
            @current-change="loadLogs"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 成员列表弹窗 -->
    <el-dialog v-model="showMembers" title="团队成员" width="500px">
      <el-table :data="teamMembersList" stripe>
        <el-table-column prop="user_id" label="UID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="row.role === 'owner' ? 'danger' : row.role === 'admin' ? 'warning' : 'info'" size="small">
              {{ row.role === 'owner' ? '组长' : row.role === 'admin' ? '管理员' : '成员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button v-if="row.role !== 'owner'" size="small" type="danger" text @click="removeMember(row)">移除</el-button>
            <span v-else style="color:#909399;font-size:12px">组长</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 团队统计弹窗 -->
    <el-dialog v-model="showTeamStats" :title="statsTeamName + ' — 学习统计'" width="700px">
      <el-table :data="teamStatsData" stripe>
        <el-table-column prop="username" label="成员" width="100" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">{{ row.role === 'owner' ? '组长' : '成员' }}</template>
        </el-table-column>
        <el-table-column label="任务完成" width="100" align="center">
          <template #default="{ row }">{{ row.tasks_done }}/{{ row.tasks_total }}</template>
        </el-table-column>
        <el-table-column prop="study_minutes" label="学习时长(min)" width="120" align="center" />
        <el-table-column label="单词掌握" width="100" align="center">
          <template #default="{ row }">{{ row.words_learned }}/{{ row.words_total }}</template>
        </el-table-column>
        <el-table-column prop="pomodoro_count" label="番茄钟数" width="100" align="center" />
      </el-table>
    </el-dialog>

    <!-- 转移组长弹窗 -->
    <el-dialog v-model="showTransfer" title="转移组长" width="400px">
      <p style="margin-bottom:12px">选择新组长：</p>
      <el-select v-model="transferUserId" placeholder="选择成员" style="width:100%">
        <el-option v-for="m in transferMembers" :key="m.user_id" :label="m.username" :value="m.user_id" />
      </el-select>
      <template #footer>
        <el-button @click="showTransfer = false">取消</el-button>
        <el-button type="primary" @click="doTransfer">确认转移</el-button>
      </template>
    </el-dialog>

    <!-- 发布公告弹窗 -->
    <el-dialog v-model="showAnnounce" title="发布公告" width="500px">
      <el-form :model="announceForm" label-width="60px">
        <el-form-item label="标题"><el-input v-model="announceForm.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="announceForm.content" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAnnounce = false">取消</el-button>
        <el-button type="primary" @click="doAnnounce">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { User, Finished, Collection, Timer, ChatDotRound, Reading } from "@element-plus/icons-vue";
import dayjs from "dayjs";
import { adminApi } from "../api";
import { useUserStore } from "../stores/user";

const store = useUserStore();
const activeTab = ref("overview");

// ===== 概览 =====
const stats = ref({});
const statCards = computed(() => [
  { label: "总用户", value: stats.value.total_users ?? 0, icon: User, color: "#409eff" },
  { label: "今日活跃", value: stats.value.today_active ?? 0, icon: Timer, color: "#67c23a" },
  { label: "总任务", value: stats.value.total_tasks ?? 0, icon: Finished, color: "#e6a23c" },
  { label: "已完成", value: stats.value.completed_tasks ?? 0, icon: Collection, color: "#f56c6c" },
  { label: "团队数", value: stats.value.total_teams ?? 0, icon: ChatDotRound, color: "#909399" },
  { label: "总单词", value: stats.value.total_words ?? 0, icon: Reading, color: "#b37feb" },
]);

// ===== 用户管理 =====
const users = ref([]);
const userSearch = ref("");
const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value;
  const kw = userSearch.value.toLowerCase();
  return users.value.filter(u => u.username.toLowerCase().includes(kw) || u.email.toLowerCase().includes(kw));
});

// ===== 团队审核 =====
const teams = ref([]);
const announcements = ref([]);
const showMembers = ref(false);
const teamMembersList = ref([]);
const currentTeamId = ref(null);
const showTeamStats = ref(false);
const teamStatsData = ref([]);
const statsTeamName = ref("");
const showTransfer = ref(false);
const transferUserId = ref(null);
const transferMembers = ref([]);
const transferTeamId = ref(null);
const showAnnounce = ref(false);
const announceForm = ref({ title: "", content: "" });
const announceTeamId = ref(null);

// ===== 操作日志 =====
const logs = ref([]);
const logPage = ref(1);
const logSize = 20;
const logTotal = ref(0);

// ===== 工具函数 =====
function fmtDate(d) { return d ? dayjs(d).format("YYYY-MM-DD") : ""; }
function fmtDateTime(d) { return d ? dayjs(d).format("YYYY-MM-DD HH:mm:ss") : ""; }

const ACTION_MAP = {
  toggle_disable: "禁用/启用", reset_password: "重置密码", delete_user: "删除用户",
  dissolve_team: "解散团队", transfer_owner: "转移组长", remove_member: "移除成员",
  publish_announcement: "发布公告", delete_announcement: "删除公告", export_data: "导出数据",
};
function actionLabel(a) { return ACTION_MAP[a] || a; }
function actionTagType(a) {
  if (["delete_user", "dissolve_team", "delete_announcement"].includes(a)) return "danger";
  if (["toggle_disable", "remove_member"].includes(a)) return "warning";
  if (a === "reset_password") return "primary";
  return "info";
}

// ===== 数据加载 =====
async function loadAll() {
  const [uRes, sRes, tRes, aRes] = await Promise.all([
    adminApi.listUsers(store.userId),
    adminApi.stats(store.userId),
    adminApi.listTeams(store.userId),
    adminApi.listAnnouncements(store.userId),
  ]);
  users.value = uRes.data;
  stats.value = sRes.data;
  teams.value = tRes.data;
  announcements.value = aRes.data;
}

async function loadLogs() {
  const [lRes, cRes] = await Promise.all([
    adminApi.listLogs(store.userId, logPage.value, logSize),
    adminApi.logsCount(store.userId),
  ]);
  logs.value = lRes.data;
  logTotal.value = cRes.data.total;
}

// ===== 用户操作 =====
async function toggleDisable(user) {
  const action = user.is_disabled ? "启用" : "禁用";
  await ElMessageBox.confirm(`确定${action}用户 ${user.username}？`, "提示", { type: "warning" });
  await adminApi.toggleDisable(user.id, store.userId);
  ElMessage.success(`已${action}`);
  loadAll();
}

async function resetPwd(user) {
  await ElMessageBox.confirm(`确定重置用户 ${user.username} 的密码为 888888？`, "重置密码", { type: "warning" });
  await adminApi.resetPassword(user.id, store.userId);
  ElMessage.success(`密码已重置为 888888`);
}

async function deleteUser(user) {
  await ElMessageBox.confirm(`确定删除用户 ${user.username}？该操作不可恢复！`, "危险操作", { type: "error" });
  await adminApi.deleteUser(user.id, store.userId);
  ElMessage.success("已删除");
  loadAll();
}

// ===== 团队操作 =====
async function viewTeamMembers(team) {
  currentTeamId.value = team.id;
  const { data } = await adminApi.teamMembers(team.id, store.userId);
  teamMembersList.value = data;
  showMembers.value = true;
}

async function removeMember(member) {
  await ElMessageBox.confirm(`确定移除成员 ${member.username}？`, "提示", { type: "warning" });
  await adminApi.removeMember(currentTeamId.value, member.user_id, store.userId);
  ElMessage.success("已移除");
  const { data } = await adminApi.teamMembers(currentTeamId.value, store.userId);
  teamMembersList.value = data;
  loadAll();
}

async function viewTeamStats(team) {
  const { data } = await adminApi.teamStats(team.id, store.userId);
  statsTeamName.value = data.team_name;
  teamStatsData.value = data.members;
  showTeamStats.value = true;
}

function openTransfer(team) {
  transferTeamId.value = team.id;
  transferUserId.value = null;
  adminApi.teamMembers(team.id, store.userId).then(({ data }) => {
    transferMembers.value = data.filter(m => m.role !== "owner");
  });
  showTransfer.value = true;
}

async function doTransfer() {
  if (!transferUserId.value) { ElMessage.warning("请选择新组长"); return; }
  await adminApi.transferOwner(transferTeamId.value, transferUserId.value, store.userId);
  ElMessage.success("组长已转移");
  showTransfer.value = false;
  loadAll();
}

function openAnnounce(team) {
  announceTeamId.value = team?.id || null;
  announceForm.value = { title: "", content: "" };
  showAnnounce.value = true;
}

async function doAnnounce() {
  if (!announceForm.value.title.trim() || !announceForm.value.content.trim()) {
    ElMessage.warning("请填写标题和内容"); return;
  }
  await adminApi.createAnnouncement({ ...announceForm.value, team_id: announceTeamId.value }, store.userId);
  ElMessage.success("公告已发布");
  showAnnounce.value = false;
  loadAll();
}

async function deleteAnnounce(ann) {
  await ElMessageBox.confirm(`确定删除公告「${ann.title}」？`, "提示", { type: "warning" });
  await adminApi.deleteAnnouncement(ann.id, store.userId);
  ElMessage.success("已删除");
  loadAll();
}

async function dissolveTeam(team) {
  await ElMessageBox.confirm(`确定解散团队「${team.name}」？所有成员关系将被清除！`, "危险操作", { type: "error" });
  await adminApi.dissolveTeam(team.id, store.userId);
  ElMessage.success("团队已解散");
  loadAll();
}

// ===== 数据导出 =====
async function exportData() {
  try {
    const { data } = await adminApi.exportData(store.userId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `taskcanvas_export_${dayjs().format("YYYY-MM-DD")}.json`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("数据导出成功");
  } catch { ElMessage.error("导出失败"); }
}

onMounted(() => {
  loadAll();
  loadLogs();
});
</script>

<style scoped>
.admin-page { max-width: 1400px; margin: 0 auto; }
.page-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }

.admin-tabs :deep(.el-tabs__header) { margin-bottom: 20px; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  display: flex; align-items: center; gap: 16px;
  padding: 20px; background: #fff;
  border-radius: var(--radius-md); box-shadow: var(--shadow-sm);
}
.stat-icon {
  width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
}
.stat-value { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }

.export-section {
  display: flex; align-items: center; gap: 16px;
  padding: 20px; background: #fafafa;
  border-radius: var(--radius-md); border: 1px dashed #dcdfe6;
}
.export-tip { font-size: 13px; color: var(--text-secondary); }

.tab-toolbar { margin-bottom: 16px; display: flex; justify-content: flex-end; }

.section-title {
  display: flex; align-items: center; justify-content: space-between;
  margin: 28px 0 12px; font-size: 16px; font-weight: 600; color: var(--text-primary);
}

.pagination-wrap { display: flex; justify-content: center; margin-top: 20px; }

.table-scroll { overflow-x: auto; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .stat-card { padding: 14px; }
  .stat-icon { width: 44px; height: 44px; }
  .stat-value { font-size: 22px; }
  .page-header { flex-wrap: wrap; }
  .export-section { flex-direction: column; align-items: flex-start; }
  .tab-toolbar :deep(.el-input) { width: 100% !important; }
}
@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
