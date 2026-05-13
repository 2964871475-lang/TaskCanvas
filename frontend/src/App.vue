<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left">
        <button class="hamburger-btn" @click="drawerVisible = true">☰</button>
        <router-link to="/" class="logo">TaskCanvas</router-link>
      </div>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path" class="nav-menu">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/tasks">任务看板</el-menu-item>
        <el-menu-item index="/vocabulary">
          单词学习
          <el-badge v-if="store.isLoggedIn && reviewCount > 0" :value="reviewCount" :max="99" class="review-badge" />
        </el-menu-item>
        <el-menu-item index="/habits">习惯打卡</el-menu-item>
        <el-menu-item index="/dashboard">数据驾驶舱</el-menu-item>
        <el-menu-item index="/team">团队</el-menu-item>
        <el-menu-item v-if="store.isAdmin" index="/admin">管理后台</el-menu-item>
      </el-menu>
      <div class="header-right">
        <router-link v-if="!store.isLoggedIn" to="/login">
          <el-button type="primary" size="small">登录</el-button>
        </router-link>
        <el-dropdown v-else>
          <span class="user-info">{{ store.username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">个人档案</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>

  <!-- 移动端侧边菜单 -->
  <el-drawer v-model="drawerVisible" direction="ltr" size="260px" :show-close="false">
    <template #header>
      <span style="font-size:18px;font-weight:700;color:var(--primary)">TaskCanvas</span>
    </template>
    <el-menu :default-active="$route.path" @select="onDrawerSelect">
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/tasks">任务看板</el-menu-item>
      <el-menu-item index="/vocabulary">
        单词学习
        <el-badge v-if="store.isLoggedIn && reviewCount > 0" :value="reviewCount" :max="99" style="margin-left:8px" />
      </el-menu-item>
      <el-menu-item index="/habits">习惯打卡</el-menu-item>
      <el-menu-item index="/dashboard">数据驾驶舱</el-menu-item>
      <el-menu-item index="/team">团队</el-menu-item>
      <el-menu-item v-if="store.isAdmin" index="/admin">管理后台</el-menu-item>
      <el-divider />
      <el-menu-item v-if="store.isLoggedIn" index="/profile">个人档案</el-menu-item>
      <el-menu-item v-if="store.isLoggedIn" index="logout">退出登录</el-menu-item>
      <el-menu-item v-if="!store.isLoggedIn" index="/login">登录</el-menu-item>
    </el-menu>
  </el-drawer>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "./stores/user";
import { vocabApi } from "./api";

const router = useRouter();
const store = useUserStore();
const reviewCount = ref(0);
const drawerVisible = ref(false);

function onDrawerSelect(index) {
  drawerVisible.value = false;
  if (index === "logout") {
    handleLogout();
  } else {
    router.push(index);
  }
}

async function loadReviewCount() {
  if (!store.isLoggedIn) return;
  try {
    const { data } = await vocabApi.getReviewCount(store.userId);
    reviewCount.value = data.count;
  } catch { /* ignore */ }
}

function handleLogout() {
  store.logout();
  reviewCount.value = 0;
  router.push("/login");
}

onMounted(loadReviewCount);
</script>

<style scoped>
.nav-menu :deep(.el-menu-item.is-active) {
  color: var(--primary);
  font-weight: 600;
}
.review-badge { margin-left: 4px; }
.review-badge :deep(.el-badge__content) { top: -2px; }
.hamburger-btn {
  display: none;
  align-items: center; justify-content: center;
  width: 36px; height: 36px;
  font-size: 22px; cursor: pointer;
  background: none; border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  margin-right: 12px;
}
</style>
