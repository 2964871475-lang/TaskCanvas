<template>
  <div class="home">
    <div class="hero">
      <h1>TaskCanvas</h1>
      <p class="subtitle">智适应学习任务管理平台</p>
      <p class="desc">任务管理 + 单词学习 + 习惯养成 + 数据可视化，一站式考研学习助手</p>
      <div class="hero-actions">
        <el-button type="primary" size="large" @click="$router.push('/tasks')">开始使用</el-button>
        <el-button size="large" @click="$router.push('/dashboard')">查看数据</el-button>
      </div>
    </div>
    <div class="features">
      <el-row :gutter="20">
        <el-col :span="6" v-for="f in features" :key="f.title">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">{{ f.icon }}</div>
            <h3>{{ f.title }}</h3>
            <p>{{ f.desc }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
const features = [
  { icon: "📋", title: "智能任务看板", desc: "拖拽排序、优先级管理、考研倒计时、连续打卡" },
  { icon: "📚", title: "单词趣味学习", desc: "艾宾浩斯曲线复习、错题本、单词连连看" },
  { icon: "⏱️", title: "番茄钟 & 习惯", desc: "专注计时、习惯打卡、小组排行榜" },
  { icon: "📊", title: "数据驾驶舱", desc: "学习趋势图、掌握度热力图、周报导出" },
];
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 80px 0 40px;
}
.hero h1 {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 8px;
}
.subtitle {
  font-size: 20px;
  color: #606266;
  margin-bottom: 12px;
}
.desc {
  color: #909399;
  margin-bottom: 24px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.features {
  margin-top: 40px;
}
.feature-card {
  text-align: center;
  padding: 20px;
}
.feature-icon {
  font-size: 40px;
  margin-bottom: 12px;
}
.feature-card h3 {
  margin-bottom: 8px;
  color: #303133;
}
.feature-card p {
  color: #909399;
  font-size: 14px;
}
</style>
