<template>
  <div class="vocab-page">
    <h1 class="page-title">单词学习</h1>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>我的词书</template>
          <div v-for="book in books" :key="book.id" class="book-item" @click="selectBook(book)">
            <span>{{ book.name }}</span>
            <el-tag size="small">{{ book.word_count || 0 }}词</el-tag>
          </div>
          <el-button type="primary" text @click="showAddBook = true">+ 新建词书</el-button>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ currentBook ? currentBook.name : "选择词书开始学习" }}</span>
              <el-button type="primary" size="small" @click="startReview" :disabled="!currentBook">
                开始复习
              </el-button>
            </div>
          </template>
          <div v-if="reviewMode">
            <div class="review-card">
              <div class="word-display">
                <h2>{{ currentWord?.english }}</h2>
                <p class="phonetic">{{ currentWord?.phonetic }}</p>
                <div v-if="showAnswer" class="answer">
                  <p>{{ currentWord?.chinese }}</p>
                  <p class="example">{{ currentWord?.example }}</p>
                </div>
              </div>
              <div class="review-actions">
                <el-button v-if="!showAnswer" @click="showAnswer = true">显示释义</el-button>
                <template v-else>
                  <el-button type="danger" @click="answerWord(false)">不认识</el-button>
                  <el-button type="success" @click="answerWord(true)">认识</el-button>
                </template>
              </div>
            </div>
          </div>
          <el-table v-else :data="words" stripe>
            <el-table-column prop="english" label="英文" width="150" />
            <el-table-column prop="chinese" label="中文" />
            <el-table-column prop="mastery" label="掌握度" width="100">
              <template #default="{ row }">
                <el-progress :percentage="row.mastery" :stroke-width="8" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showAddBook" title="新建词书">
      <el-form :model="newBook">
        <el-form-item label="词书名称"><el-input v-model="newBook.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="newBook.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddBook = false">取消</el-button>
        <el-button type="primary" @click="createBook">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { vocabApi } from "../api";

const books = ref([]);
const words = ref([]);
const currentBook = ref(null);
const reviewMode = ref(false);
const currentWord = ref(null);
const showAnswer = ref(false);
const showAddBook = ref(false);
const newBook = ref({ name: "", description: "" });
const reviewWords = ref([]);
const reviewIndex = ref(0);

function getUser() {
  return JSON.parse(localStorage.getItem("user") || "{}");
}

async function loadBooks() {
  const user = getUser();
  if (!user.id) return;
  const { data } = await vocabApi.listBooks(user.id);
  books.value = data;
}

async function selectBook(book) {
  currentBook.value = book;
  reviewMode.value = false;
  const { data } = await vocabApi.listWords(book.id);
  words.value = data;
}

async function createBook() {
  const user = getUser();
  await vocabApi.createBook({ ...newBook.value, user_id: user.id });
  showAddBook.value = false;
  loadBooks();
}

async function startReview() {
  const user = getUser();
  const { data } = await vocabApi.getReview(user.id, 20);
  reviewWords.value = data;
  reviewIndex.value = 0;
  reviewMode.value = true;
  showAnswer.value = false;
  currentWord.value = reviewWords.value[0] || null;
}

async function answerWord(isCorrect) {
  if (!currentWord.value) return;
  await vocabApi.answer(currentWord.value.id, isCorrect);
  reviewIndex.value++;
  if (reviewIndex.value < reviewWords.value.length) {
    currentWord.value = reviewWords.value[reviewIndex.value];
    showAnswer.value = false;
  } else {
    reviewMode.value = false;
    if (currentBook.value) selectBook(currentBook.value);
  }
}

onMounted(loadBooks);
</script>

<style scoped>
.book-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}
.book-item:hover {
  background: #f5f7fa;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.review-card {
  text-align: center;
  padding: 40px;
}
.word-display h2 {
  font-size: 36px;
  margin-bottom: 8px;
}
.phonetic {
  color: #909399;
  margin-bottom: 20px;
}
.answer {
  margin: 20px 0;
}
.example {
  color: #909399;
  font-style: italic;
  margin-top: 8px;
}
.review-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
