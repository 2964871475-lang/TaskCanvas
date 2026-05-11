<template>
  <div class="team-page">
    <h1 class="page-title">团队管理</h1>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>创建团队</template>
          <el-form :model="newTeam">
            <el-form-item label="团队名称"><el-input v-model="newTeam.name" /></el-form-item>
            <el-form-item label="描述"><el-input v-model="newTeam.description" type="textarea" /></el-form-item>
            <el-form-item>
              <el-button type="primary" @click="createTeam">创建</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>加入团队</template>
          <el-form>
            <el-form-item label="邀请码"><el-input v-model="inviteCode" placeholder="输入邀请码" /></el-form-item>
            <el-form-item>
              <el-button type="success" @click="joinTeam">加入</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { userApi } from "../api";

const newTeam = ref({ name: "", description: "" });
const inviteCode = ref("");

function getUser() {
  return JSON.parse(localStorage.getItem("user") || "{}");
}

async function createTeam() {
  const user = getUser();
  if (!user.id) return ElMessage.warning("请先登录");
  const { data } = await userApi.createTeam(newTeam.value, user.id);
  ElMessage.success(`团队创建成功！邀请码：${data.invite_code}`);
}

async function joinTeam() {
  const user = getUser();
  if (!user.id) return ElMessage.warning("请先登录");
  await userApi.joinTeam(inviteCode.value, user.id);
  ElMessage.success("加入团队成功");
}
</script>
