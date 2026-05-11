<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>{{ isRegister ? "注册" : "登录" }}</h2>
      <el-form :model="form" @submit.prevent="handleSubmit">
        <el-form-item v-if="isRegister">
          <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading" style="width:100%">
            {{ isRegister ? "注册" : "登录" }}
          </el-button>
        </el-form-item>
      </el-form>
      <div class="switch-mode">
        <el-link type="primary" @click="isRegister = !isRegister">
          {{ isRegister ? "已有账号？去登录" : "没有账号？去注册" }}
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { userApi } from "../api";

const router = useRouter();
const isRegister = ref(false);
const loading = ref(false);
const form = ref({ username: "", password: "", email: "" });

async function handleSubmit() {
  loading.value = true;
  try {
    if (isRegister.value) {
      await userApi.register(form.value);
      ElMessage.success("注册成功，请登录");
      isRegister.value = false;
    } else {
      const { data } = await userApi.login(form.value);
      localStorage.setItem("user", JSON.stringify(data));
      ElMessage.success("登录成功");
      router.push("/");
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || "操作失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
.login-card {
  width: 400px;
  padding: 20px;
}
.login-card h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #303133;
}
.switch-mode {
  text-align: center;
}
</style>
