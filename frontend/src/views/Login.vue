<template>
  <div class="login-page">
    <div class="login-left" @mousemove="onMouseMove" ref="leftRef">
      <div class="left-glow" :style="glowStyle"></div>
      <div class="brand-content">
        <h1 class="animated-title">TaskCanvas</h1>
        <p class="brand-subtitle">智适应学习任务管理平台</p>
        <div class="brand-features">
          <div class="brand-feature" v-for="(f, i) in features" :key="f.text" :style="{ animationDelay: i * 0.15 + 's' }">
            <span class="bf-icon">{{ f.icon }}</span>
            <span>{{ f.text }}</span>
          </div>
        </div>
      </div>
      <div class="floating-shapes">
        <span v-for="i in 5" :key="i" class="shape" :class="'shape-' + i"></span>
      </div>
    </div>
    <div class="login-right">
      <el-card class="login-card" shadow="never">
        <h2>{{ isRegister ? "创建账号" : "欢迎回来" }}</h2>
        <p class="form-subtitle">{{ isRegister ? "注册后即可开始使用" : "登录以继续你的学习之旅" }}</p>
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
          <el-form-item v-if="isRegister" prop="email">
            <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" size="large" />
          </el-form-item>
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password size="large" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading" size="large" style="width:100%">
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { userApi } from "../api";
import { useUserStore } from "../stores/user";

const router = useRouter();
const route = useRoute();
const store = useUserStore();
const isRegister = ref(false);
const loading = ref(false);
const formRef = ref(null);
const leftRef = ref(null);
const form = reactive({ username: "", password: "", email: "" });

const mouseX = ref(50);
const mouseY = ref(50);
const glowStyle = computed(() => ({
  background: `radial-gradient(circle 250px at ${mouseX.value}% ${mouseY.value}%, rgba(255,255,255,0.12), transparent)`,
}));

function onMouseMove(e) {
  if (!leftRef.value) return;
  const rect = leftRef.value.getBoundingClientRect();
  mouseX.value = ((e.clientX - rect.left) / rect.width) * 100;
  mouseY.value = ((e.clientY - rect.top) / rect.height) * 100;
}

const features = [
  { icon: "📋", text: "智能任务看板，拖拽排序" },
  { icon: "📚", text: "艾宾浩斯单词复习" },
  { icon: "⏱️", text: "番茄钟专注计时" },
  { icon: "📊", text: "学习数据可视化" },
];

const rules = reactive({
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 2, max: 20, message: "用户名长度需在 2-20 个字符之间", trigger: "blur" },
    { pattern: /^[a-zA-Z0-9_一-鿿]+$/, message: "用户名只能包含字母、数字、下划线或中文", trigger: "blur" }
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 50, message: "密码长度需在 6-50 个字符之间", trigger: "blur" }
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入有效的邮箱地址", trigger: "blur" }
  ]
});

watch(isRegister, () => {
  formRef.value?.clearValidate();
});

async function handleSubmit() {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();
  } catch {
    return;
  }
  loading.value = true;
  try {
    if (isRegister.value) {
      await userApi.register({ ...form });
      ElMessage.success("注册成功，请登录");
      isRegister.value = false;
    } else {
      const { data } = await userApi.login({ username: form.username, password: form.password });
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
  min-height: calc(100vh - 108px);
  margin: -24px;
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.left-glow {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  transition: background 0.3s ease;
}

.floating-shapes { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  animation: floatUp linear infinite;
}
.shape-1 { width: 60px; height: 60px; left: 15%; bottom: -60px; animation-duration: 11s; }
.shape-2 { width: 100px; height: 100px; left: 40%; bottom: -100px; animation-duration: 14s; animation-delay: 2s; }
.shape-3 { width: 45px; height: 45px; left: 65%; bottom: -45px; animation-duration: 9s; animation-delay: 1s; }
.shape-4 { width: 70px; height: 70px; left: 80%; bottom: -70px; animation-duration: 12s; animation-delay: 3s; }
.shape-5 { width: 55px; height: 55px; left: 25%; bottom: -55px; animation-duration: 10s; animation-delay: 4s; }

@keyframes floatUp {
  0% { transform: translateY(0) rotate(0deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-500px) rotate(360deg); opacity: 0; }
}

.brand-content { position: relative; z-index: 2; }

.animated-title {
  font-size: 42px;
  margin-bottom: 12px;
  letter-spacing: 2px;
  background: linear-gradient(90deg, #fff, #a8edea, #fed6e3, #fff);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: titleShimmer 4s ease-in-out infinite;
}

@keyframes titleShimmer {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.brand-subtitle { font-size: 20px; opacity: 0.85; margin-bottom: 40px; }
.brand-features { display: flex; flex-direction: column; gap: 16px; }
.brand-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  opacity: 0;
  animation: featureSlideIn 0.5s ease forwards;
}

@keyframes featureSlideIn {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 0.85; transform: translateX(0); }
}

.bf-icon { font-size: 22px; }

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}

.login-card { width: 420px; border: none; }
.login-card :deep(.el-card__body) { padding: 40px 32px; }
.login-card h2 { text-align: center; font-size: 26px; color: var(--text-primary); margin-bottom: 8px; }
.form-subtitle { text-align: center; color: var(--text-secondary); margin-bottom: 28px; font-size: 14px; }
.switch-mode { text-align: center; margin-top: 8px; }
</style>
