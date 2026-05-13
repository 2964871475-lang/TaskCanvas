<template>
  <div class="profile-page">
    <h1 class="page-title">个人档案</h1>
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card>
          <template #header>基本信息</template>
          <el-form :model="form" label-width="80px">
            <el-form-item label="用户名"><el-input v-model="form.username" disabled /></el-form-item>
            <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
            <el-form-item label="头像URL"><el-input v-model="form.avatar" placeholder="输入图片URL" /></el-form-item>
            <el-form-item label="简介"><el-input v-model="form.bio" type="textarea" :rows="3" /></el-form-item>
            <el-form-item><el-button type="primary" @click="saveProfile">保存修改</el-button></el-form-item>
          </el-form>
        </el-card>
        <el-card style="margin-top:16px">
          <template #header>修改密码</template>
          <el-form :model="pwForm" label-width="80px">
            <el-form-item label="原密码"><el-input v-model="pwForm.old_password" type="password" show-password /></el-form-item>
            <el-form-item label="新密码"><el-input v-model="pwForm.new_password" type="password" show-password /></el-form-item>
            <el-form-item><el-button type="warning" @click="changePassword">修改密码</el-button></el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card>
          <template #header>学习概览</template>
          <el-row :gutter="16">
            <el-col :span="8" v-for="s in stats" :key="s.label">
              <div class="stat-box">
                <div class="stat-val">{{ s.value }}</div>
                <div class="stat-lbl">{{ s.label }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useUserStore } from "../stores/user";
import { userApi, statsApi } from "../api";

const store = useUserStore();
const form = ref({ username: "", email: "", avatar: "", bio: "" });
const pwForm = ref({ old_password: "", new_password: "" });
const stats = ref([]);

onMounted(async () => {
  if (store.userId) {
    const { data } = await userApi.getUser(store.userId);
    form.value = { username: data.username, email: data.email, avatar: data.avatar, bio: data.bio };
    const { data: ov } = await statsApi.overview(store.userId);
    stats.value = [
      { label: "总任务", value: ov.total_tasks },
      { label: "完成率", value: ov.completion_rate + "%" },
      { label: "掌握单词", value: ov.mastered_words + "/" + ov.total_words },
    ];
  }
});

async function saveProfile() {
  await userApi.updateProfile(store.userId, { email: form.value.email, avatar: form.value.avatar, bio: form.value.bio });
  store.updateProfile({ email: form.value.email, avatar: form.value.avatar, bio: form.value.bio });
  ElMessage.success("保存成功");
}

async function changePassword() {
  await userApi.changePassword(store.userId, pwForm.value);
  ElMessage.success("密码修改成功");
  pwForm.value = { old_password: "", new_password: "" };
}
</script>

<style scoped>
.profile-page { max-width: 900px; margin: 0 auto; }
.stat-box { text-align: center; padding: 16px; }
.stat-val { font-size: 28px; font-weight: 700; color: #409eff; }
.stat-lbl { color: #909399; margin-top: 4px; }
</style>
