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
              <div class="team-name">{{ team.name }}</div>
              <div class="team-desc">{{ team.description || "暂无描述" }}</div>
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
              <el-tag :type="m.role === 'owner' ? 'danger' : 'info'" size="small">{{ m.role === 'owner' ? '队长' : '成员' }}</el-tag>
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
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useUserStore } from "../stores/user";
import { userApi } from "../api";

const store = useUserStore();
const myTeams = ref([]);
const selectedTeam = ref(null);
const members = ref([]);
const inviteCode = ref("");
const newTeam = ref({ name: "", description: "" });

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
  const { data } = await userApi.createTeam(newTeam.value, store.userId);
  ElMessage.success(`创建成功！邀请码：${data.invite_code}`);
  newTeam.value = { name: "", description: "" };
  loadTeams();
}

async function joinTeam() {
  await userApi.joinTeam(inviteCode.value, store.userId);
  ElMessage.success("加入成功");
  inviteCode.value = "";
  loadTeams();
}
</script>

<style scoped>
.team-row { align-items: stretch; }
.team-col { display: flex; flex-direction: column; gap: 16px; }
.team-card { flex: 1; min-height: 200px; display: flex; flex-direction: column; }

/* 团队列表 */
.team-list { min-height: 60px; }
.team-item { padding: 10px 12px; cursor: pointer; border-radius: 6px; margin-bottom: 4px; transition: background .2s; border: 1px solid #ebeef5; }
.team-item:hover { background: #f0f5ff; border-color: #b3d8ff; }
.team-item.active { background: #ecf5ff; border-color: #409eff; }
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
</style>
