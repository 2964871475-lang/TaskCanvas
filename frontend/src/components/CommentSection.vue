<template>
  <div class="comment-section">
    <div class="comment-list">
      <div v-for="c in comments" :key="c.id" class="comment-item">
        <div class="comment-header">
          <span class="comment-user">{{ c.username }}</span>
          <span class="comment-time">{{ formatTime(c.created_at) }}</span>
          <el-button v-if="c.user_id === userId" type="danger" text size="small" @click="remove(c.id)">删除</el-button>
        </div>
        <div class="comment-body">{{ c.content }}</div>
      </div>
      <el-empty v-if="!comments.length" description="暂无评论" :image-size="60" />
    </div>
    <div class="comment-input">
      <el-input v-model="newComment" placeholder="写下你的评论..." @keyup.enter="submit">
        <template #append><el-button @click="submit">发送</el-button></template>
      </el-input>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { commentApi } from "../api";
import { useUserStore } from "../stores/user";
import dayjs from "dayjs";

const props = defineProps({ taskId: { type: Number, required: true } });
const store = useUserStore();
const userId = store.userId;
const comments = ref([]);
const newComment = ref("");

function formatTime(t) { return dayjs(t).format("MM-DD HH:mm"); }

async function load() {
  const { data } = await commentApi.list(props.taskId);
  comments.value = data;
}

async function submit() {
  if (!newComment.value.trim()) return;
  await commentApi.create({ content: newComment.value, task_id: props.taskId, user_id: userId });
  newComment.value = "";
  load();
}

async function remove(id) {
  await commentApi.delete(id);
  load();
}

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.comment-section { margin-top: 8px; }
.comment-list { max-height: 200px; overflow-y: auto; margin-bottom: 8px; }
.comment-item { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.comment-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.comment-user { font-weight: 600; font-size: 13px; }
.comment-time { color: #909399; font-size: 12px; }
.comment-body { font-size: 14px; color: #606266; }
</style>
