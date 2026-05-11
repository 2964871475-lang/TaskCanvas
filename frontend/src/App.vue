<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">TaskCanvas</router-link>
      </div>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path" class="nav-menu">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/tasks">任务看板</el-menu-item>
        <el-menu-item index="/vocabulary">单词学习</el-menu-item>
        <el-menu-item index="/habits">习惯打卡</el-menu-item>
        <el-menu-item index="/dashboard">数据驾驶舱</el-menu-item>
        <el-menu-item index="/team">团队</el-menu-item>
      </el-menu>
      <div class="header-right">
        <router-link v-if="!user" to="/login">
          <el-button type="primary" size="small">登录</el-button>
        </router-link>
        <el-dropdown v-else>
          <span class="user-info">{{ user.username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const user = ref(null);

onMounted(() => {
  const saved = localStorage.getItem("user");
  if (saved) user.value = JSON.parse(saved);
});

function logout() {
  localStorage.removeItem("user");
  user.value = null;
  router.push("/login");
}
</script>
