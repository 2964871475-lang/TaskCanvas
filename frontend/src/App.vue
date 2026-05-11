<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">
          <span class="logo-icon">📚</span>
          <span>TaskCanvas</span>
        </router-link>
      </div>
      <el-menu
        mode="horizontal"
        :router="true"
        :default-active="$route.path"
        class="nav-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务看板</span>
        </el-menu-item>
        <el-menu-item index="/vocabulary">
          <el-icon><Reading /></el-icon>
          <span>单词学习</span>
        </el-menu-item>
        <el-menu-item index="/habits">
          <el-icon><Timer /></el-icon>
          <span>习惯打卡</span>
        </el-menu-item>
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据驾驶舱</span>
        </el-menu-item>
        <el-menu-item index="/team">
          <el-icon><User /></el-icon>
          <span>团队</span>
        </el-menu-item>
      </el-menu>
      <div class="header-right">
        <router-link v-if="!store.isLoggedIn" to="/login">
          <el-button type="primary" size="default">登录</el-button>
        </router-link>
        <el-dropdown v-else trigger="click">
          <div class="user-avatar">
            <span class="avatar-text">{{ store.username?.charAt(0)?.toUpperCase() }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">
                <el-icon><User /></el-icon>
                个人档案
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
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
import { useRouter } from "vue-router";
import { useUserStore } from "./stores/user";
import {
  HomeFilled,
  List,
  Reading,
  Timer,
  DataLine,
  User,
  SwitchButton
} from "@element-plus/icons-vue";

const router = useRouter();
const store = useUserStore();

function handleLogout() {
  store.logout();
  router.push("/login");
}
</script>

<style scoped>
/* User avatar */
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-avatar:hover {
  background: var(--primary-light);
  transform: scale(1.05);
}

.avatar-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}
</style>
