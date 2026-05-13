<template>
  <div class="vocab-page">
    <h1 class="page-title">单词学习</h1>

    <el-tabs v-model="activeTab">
      <!-- 词书管理 -->
      <el-tab-pane label="词书管理" name="books">
        <el-row :gutter="20" class="vocab-row">
          <!-- 左侧：词书列表 -->
          <el-col :xs="24" :sm="8" :md="5">
            <el-card class="vocab-card book-panel" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>我的词书</span>
                  <el-button type="primary" text size="small" @click="showAddBook = true">+ 新建</el-button>
                </div>
              </template>
              <div class="book-list">
                <div v-for="book in books" :key="book.id" class="book-item" :class="{ active: currentBook?.id === book.id }" @click="selectBook(book)">
                  <div class="book-info">
                    <span class="book-name">{{ book.name }}</span>
                    <span class="book-count">{{ book.word_count || 0 }}词</span>
                  </div>
                </div>
                <el-empty v-if="!books.length" description="还没有词书" :image-size="60" />
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：单词内容 -->
          <el-col :xs="24" :sm="16" :md="19">
            <el-card class="vocab-card content-panel" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">{{ currentBook ? currentBook.name : '选择左侧词书开始' }}</span>
                  <div v-if="currentBook" class="header-buttons">
                    <el-button size="small" @click="showBatchImport = true">批量导入</el-button>
                    <el-button type="primary" size="small" @click="startReview">开始复习</el-button>
                    <el-button type="success" size="small" @click="startGame">连连看</el-button>
                  </div>
                </div>
              </template>

              <!-- 复习模式 -->
              <div v-if="reviewMode" class="review-card">
                <div class="word-display">
                  <h2>{{ currentWord?.english }}</h2>
                  <p class="phonetic">{{ currentWord?.phonetic }}</p>
                  <div v-if="showAnswer" class="answer">
                    <p>{{ currentWord?.chinese }}</p>
                    <p class="example">{{ currentWord?.example }}</p>
                  </div>
                </div>
                <div class="review-actions">
                  <el-button v-if="!showAnswer" size="large" @click="showAnswer = true">显示释义</el-button>
                  <template v-else>
                    <el-button type="danger" size="large" @click="answerWord(false)">不认识</el-button>
                    <el-button type="success" size="large" @click="answerWord(true)">认识</el-button>
                  </template>
                </div>
                <div class="review-progress">进度: {{ reviewIndex + 1 }} / {{ reviewWords.length }}</div>
              </div>

              <!-- 游戏模式 -->
              <div v-else-if="gameMode">
                <WordMatchGame :words="gameWords" @done="gameMode = false" />
              </div>

              <!-- 单词列表模式 -->
              <div v-else class="word-table-wrap">
                <el-table :data="words" stripe style="width:100%" height="100%">
                  <el-table-column prop="english" label="英文" width="180" />
                  <el-table-column prop="chinese" label="中文" />
                  <el-table-column prop="phonetic" label="音标" width="160" />
                  <el-table-column prop="mastery" label="掌握度" width="150">
                    <template #default="{ row }">
                      <el-progress :percentage="Math.round(row.mastery)" :stroke-width="8" />
                    </template>
                  </el-table-column>
                  <el-table-column label="收藏" width="70">
                    <template #default="{ row }">
                      <el-button text @click="toggleStar(row)">{{ row.is_starred ? '★' : '☆' }}</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-if="!words.length && currentBook" description="词书为空，请导入单词" :image-size="80" />
                <el-empty v-if="!currentBook" description="请从左侧选择一本词书" :image-size="80" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 错题本 -->
      <el-tab-pane label="错题本" name="errors">
        <el-card class="vocab-card" shadow="hover">
          <template #header><span>错误单词列表</span></template>
          <el-table :data="errorWords" stripe style="width:100%">
            <el-table-column prop="english" label="英文" width="180" />
            <el-table-column prop="chinese" label="中文" />
            <el-table-column prop="phonetic" label="音标" width="160" />
            <el-table-column prop="error_count" label="错误次数" width="100" />
            <el-table-column prop="mastery" label="掌握度" width="150">
              <template #default="{ row }">
                <el-progress :percentage="Math.round(row.mastery)" :stroke-width="8" />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!errorWords.length" description="暂无错题" :image-size="60" />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 新建词书对话框 -->
    <el-dialog v-model="showAddBook" title="新建词书">
      <el-form :model="newBook">
        <el-form-item label="名称"><el-input v-model="newBook.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="newBook.description" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddBook = false">取消</el-button>
        <el-button type="primary" @click="createBook">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showBatchImport" title="批量导入单词" width="500px">
      <p style="margin-bottom:8px;color:#909399">每行一个单词，格式：英文|中文|音标（音标可选）</p>
      <el-input v-model="batchText" type="textarea" :rows="8" placeholder="apple|苹果|&#x2C8;&#xE6;pl&#x259;mbaby|婴儿" />
      <template #footer>
        <el-button @click="showBatchImport = false">取消</el-button>
        <el-button type="primary" @click="batchImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { vocabApi } from "../api";
import { useUserStore } from "../stores/user";
import WordMatchGame from "../components/WordMatchGame.vue";

const store = useUserStore();
const activeTab = ref("books");
const books = ref([]);
const words = ref([]);
const errorWords = ref([]);
const currentBook = ref(null);

const reviewMode = ref(false);
const reviewWords = ref([]);
const reviewIndex = ref(0);
const currentWord = ref(null);
const showAnswer = ref(false);

const gameMode = ref(false);
const gameWords = ref([]);

const showAddBook = ref(false);
const newBook = ref({ name: "", description: "" });
const showBatchImport = ref(false);
const batchText = ref("");

async function loadBooks() {
  if (!store.userId) return;
  try { const { data } = await vocabApi.listBooks(store.userId); books.value = data; } catch {}
}

async function loadErrors() {
  if (!store.userId) return;
  try { const { data } = await vocabApi.getErrors(store.userId); errorWords.value = data; } catch {}
}

async function selectBook(book) {
  currentBook.value = book;
  reviewMode.value = false;
  gameMode.value = false;
  try { const { data } = await vocabApi.listWords(book.id); words.value = data; } catch {}
}

async function createBook() {
  await vocabApi.createBook({ ...newBook.value, user_id: store.userId });
  showAddBook.value = false;
  newBook.value = { name: "", description: "" };
  loadBooks();
}

async function startReview() {
  const { data } = await vocabApi.getReview(store.userId, 20);
  if (!data.length) { ElMessage.info("暂无待复习单词"); return; }
  reviewWords.value = data;
  reviewIndex.value = 0;
  reviewMode.value = true;
  gameMode.value = false;
  showAnswer.value = false;
  currentWord.value = data[0];
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
    ElMessage.success("复习完成！");
    if (currentBook.value) selectBook(currentBook.value);
  }
}

function startGame() {
  if (!words.value.length) { ElMessage.info("词书为空"); return; }
  gameWords.value = words.value;
  gameMode.value = true;
  reviewMode.value = false;
}

async function toggleStar(word) {
  try { await vocabApi.toggleStar(word.id); word.is_starred = !word.is_starred; } catch {}
}

async function batchImport() {
  const lines = batchText.value.trim().split("\n").filter(Boolean);
  const wordList = lines.map((line) => {
    const parts = line.split("|");
    return { english: parts[0]?.trim() || "", chinese: parts[1]?.trim() || "", phonetic: parts[2]?.trim() || "" };
  }).filter((w) => w.english && w.chinese);
  if (!wordList.length) { ElMessage.warning("无有效单词"); return; }
  await vocabApi.batchAdd(currentBook.value.id, wordList);
  ElMessage.success(`成功导入 ${wordList.length} 个单词`);
  showBatchImport.value = false;
  batchText.value = "";
  selectBook(currentBook.value);
}

onMounted(() => { loadBooks(); loadErrors(); });
</script>

<style scoped>
.vocab-page { max-width: 1600px; margin: 0 auto; }
.vocab-row { align-items: stretch; }
.vocab-card { height: 100%; display: flex; flex-direction: column; }
.book-panel { min-height: 520px; }
.content-panel { min-height: 520px; }

.card-header { display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 8px; }
.card-title { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.header-buttons { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }

/* 词书列表 */
.book-list { flex: 1; overflow-y: auto; }
.book-item { padding: 12px; cursor: pointer; border-radius: 6px; transition: background .2s; margin-bottom: 4px; border: 1px solid transparent; }
.book-item:hover { background: #f0f5ff; }
.book-item.active { background: #ecf5ff; border-color: #409eff; }
.book-info { display: flex; justify-content: space-between; align-items: center; }
.book-name { font-weight: 500; }
.book-count { font-size: 12px; color: #909399; }

/* 单词表格区域 */
.word-table-wrap { flex: 1; display: flex; flex-direction: column; min-height: 350px; }

/* 复习模式 */
.review-card { text-align: center; padding: 60px 20px; }
.word-display h2 { font-size: 42px; margin-bottom: 8px; }
.phonetic { color: #909399; margin-bottom: 20px; font-size: 16px; }
.answer { margin: 24px 0; }
.answer p:first-child { font-size: 24px; margin-bottom: 8px; }
.example { color: #909399; font-style: italic; }
.review-actions { display: flex; gap: 16px; justify-content: center; margin-bottom: 16px; }
.review-progress { color: #909399; margin-top: 12px; }

@media (max-width: 768px) {
  .vocab-row :deep(.el-col) { margin-bottom: 12px; }
  .book-panel { min-height: auto; max-height: 260px; }
  .content-panel { min-height: auto; }
  .word-table-wrap { min-height: auto; }
  .review-card { padding: 30px 12px; }
  .word-display h2 { font-size: 30px; }
  .answer p:first-child { font-size: 18px; }
  .header-buttons { flex-wrap: wrap; }
}
@media (max-width: 480px) {
  .card-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .header-buttons { width: 100%; }
  .header-buttons .el-button { flex: 1; }
  .review-actions { flex-direction: column; align-items: center; }
  .review-actions .el-button { width: 100%; }
}
</style>
