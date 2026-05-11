<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-header">
        <div class="logo-wrapper">
          <span class="logo-icon">📚</span>
          <h2 class="logo-text">TaskCanvas</h2>
        </div>
        <p class="login-subtitle">{{ isRegister ? "创建新账户" : "欢迎回来" }}</p>
      </div>

      <el-form :model="form" @submit.prevent="handleSubmit" class="login-form">
        <el-form-item v-if="isRegister">
          <el-input
            v-model="form.email"
            placeholder="邮箱地址"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="loading"
            size="large"
            class="submit-btn"
          >
            {{ isRegister ? "注册" : "登录" }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="switch-mode">
        <span class="switch-text">
          {{ isRegister ? "已有账号？" : "没有账号？" }}
        </span>
        <el-link type="primary" @click="isRegister = !isRegister">
          {{ isRegister ? "去登录" : "去注册" }}
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { userApi } from "../api";
import { useUserStore } from "../stores/user";

const router = useRouter();
const route = useRoute();
const store = useUserStore();
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
      store.setUser(data);
      ElMessage.success("登录成功");
      router.push(route.query.redirect || "/");
    }
  } catch (e) {
    // interceptor handles error display
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
  min-height: 70vh;
}

.login-card {
  width: 420px;
  padding: 16px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}

.login-subtitle {
  color: var(--text-secondary);
  font-size: 15px;
}

.login-form {
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
}

.switch-mode {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
}

.switch-text {
  color: var(--text-secondary);
}
</style>
