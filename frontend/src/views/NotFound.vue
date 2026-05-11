<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<style scoped>
.not-found { text-align: center; padding: 120px 0; }
.not-found h1 { font-size: 80px; color: #409eff; margin-bottom: 16px; }
.not-found p { font-size: 18px; color: #909399; margin-bottom: 24px; }
</style>
