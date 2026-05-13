<template>
  <div class="team-page">
    <h1 class="page-title">团队管理</h1>

    <el-row :gutter="20" class="team-row">
      <!-- 左列 -->
      <el-col :span="12" class="team-col">
        <!-- 我的团队 -->
        <el-card class="team-card" shadow="hover">
          <template #header><span>我的团队</span></template>
          <div class="team-list">
            <div v-for="team in myTeams" :key="team.id" class="team-item" :class="{ active: selectedTeam?.id === team.id }" @click="selectTeam(team)">
              <div class="team-info">
                <div class="team-name">{{ team.name }}</div>
                <div class="team-desc">{{ team.description || "暂无描述" }}</div>
              </div>
              <el-button v-if="team.owner_id === store.userId" type="danger" text size="small" @click.stop="deleteTeam(team)">删除</el-button>
            </div>
            <el-empty v-if="!myTeams.length" description="还没有加入任何团队" :image-size="60" />
          </div>
        </el-card>

        <!-- 创建团队 -->
        <el-card class="team-card" shadow="hover">
          <template #header><span>创建团队</span></template>
          <el-form :model="newTeam" label-width="50px" label-position="left">
            <el-form-item label="名称"><el-input v-model="newTeam.name" /></el-form-item>
            <el-form-item label="描述"><el-input v-model="newTeam.description" type="textarea" :rows="2" /></el-form-item>
            <el-form-item>
              <el-button type="primary" @click="createTeam">创建团队</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右列 -->
      <el-col :span="12" class="team-col">
        <!-- 团队详情 -->
        <el-card v-if="selectedTeam" class="team-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ selectedTeam.name }}</span>
              <el-tag size="small">邀请码: {{ selectedTeam.invite_code }}</el-tag>
            </div>
          </template>
          <p class="team-desc-full">{{ selectedTeam.description || "暂无描述" }}</p>
          <el-divider />
          <h4 class="section-title">成员列表</h4>
          <div class="member-list">
            <div v-for="m in members" :key="m.id" class="member-item">
              <span class="member-name">{{ m.username }}</span>
              <div class="member-actions">
                <el-tag :type="m.role === 'owner' ? 'danger' : 'info'" size="small">{{ m.role === 'owner' ? '队长' : '成员' }}</el-tag>
                <el-button v-if="isOwner && m.role !== 'owner'" type="danger" text size="small" @click="removeMember(m)">移除</el-button>
              </div>
            </div>
            <el-empty v-if="!members.length" description="暂无成员" :image-size="60" />
          </div>
        </el-card>

        <!-- 加入团队 -->
        <el-card v-else class="team-card" shadow="hover">
          <template #header><span>加入团队</span></template>
          <el-form label-width="50px" label-position="left">
            <el-form-item label="邀请码"><el-input v-model="inviteCode" placeholder="输入邀请码" /></el-form-item>
            <el-form-item>
              <el-button type="success" @click="joinTeam">加入团队</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "../stores/user";
import { userApi } from "../api";

const store = useUserStore();
const myTeams = ref([]);
const selectedTeam = ref(null);
const members = ref([]);
const inviteCode = ref("");
const newTeam = ref({ name: "", description: "" });

const isOwner = computed(() => selectedTeam.value?.owner_id === store.userId);

onMounted(loadTeams);

async function loadTeams() {
  if (!store.userId) return;
  try { const { data } = await userApi.getTeams(store.userId); myTeams.value = data; } catch {}
}

async function selectTeam(team) {
  selectedTeam.value = team;
  try { const { data } = await userApi.getTeamMembers(team.id); members.value = data; } catch {}
}

async function createTeam() {
  if (!newTeam.value.name.trim()) { ElMessage.warning("请输入团队名称"); return; }
  const { data } = await userApi.createTeam(newTeam.value, store.userId);
  ElMessage.success(`创建成功！邀请码：${data.invite_code}`);
  newTeam.value = { name: "", description: "" };
  loadTeams();
}

async function joinTeam() {
  if (!inviteCode.value.trim()) { ElMessage.warning("请输入邀请码"); return; }
  await userApi.joinTeam(inviteCode.value, store.userId);
  ElMessage.success("加入成功");
  inviteCode.value = "";
  loadTeams();
}

async function deleteTeam(team) {
  try {
    await ElMessageBox.confirm(`确定要删除团队「${team.name}」吗？删除后所有成员将被移除。`, "删除确认", { type: "warning" });
    await userApi.deleteTeam(team.id, store.userId);
    ElMessage.success("团队已删除");
    if (selectedTeam.value?.id === team.id) { selectedTeam.value = null; members.value = []; }
    loadTeams();
  } catch {}
}

async function removeMember(member) {
  try {
    await ElMessageBox.confirm(`确定要移除成员「${member.username}」吗？`, "移除确认", { type: "warning" });
    await userApi.removeMember(selectedTeam.value.id, member.user_id, store.userId);
    ElMessage.success("已移除");
    selectTeam(selectedTeam.value);
  } catch {}
}
</script>

<style scoped>
.team-page { max-width: 1200px; margin: 0 auto; }
.team-row { align-items: stretch; }
.team-col { display: flex; flex-direction: column; gap: 16px; }
.team-card { flex: 1; min-height: 200px; display: flex; flex-direction: column; }

/* 团队列表 */
.team-list { min-height: 60px; }
.team-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; cursor: pointer; border-radius: 6px; margin-bottom: 4px; transition: background .2s; border: 1px solid #ebeef5; }
.team-item:hover { background: #f0f5ff; border-color: #b3d8ff; }
.team-item.active { background: #ecf5ff; border-color: #409eff; }
.team-info { flex: 1; min-width: 0; }
.team-name { font-weight: 600; margin-bottom: 2px; }
.team-desc { font-size: 13px; color: #909399; }

/* 详情 */
.card-header { display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 8px; }
.team-desc-full { color: #606266; margin-bottom: 4px; }
.section-title { margin-bottom: 8px; color: #303133; }

/* 成员列表 */
.member-list { min-height: 40px; }
.member-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.member-item:last-child { border-bottom: none; }
.member-name { font-weight: 500; }
.member-actions { display: flex; align-items: center; gap: 8px; }
</style>
