<template>
  <div class="match-game">
    <div class="game-header">
      <span>用时: {{ formatTime(elapsed) }}</span>
      <span>得分: {{ score }}</span>
      <span>剩余: {{ pairs.length - matchedCount }}</span>
    </div>

    <!-- 游戏界面 -->
    <div v-if="!gameOver" class="game-board">
      <div class="column">
        <div
          v-for="item in leftItems" :key="item.id" class="match-card"
          :class="{ selected: selectedLeft === item.id, matched: matchedIds.has(item.id), wrong: wrongId === item.id }"
          @click="selectLeft(item)"
        >{{ item.english }}</div>
      </div>
      <div class="column">
        <div
          v-for="item in rightItems" :key="item.id" class="match-card"
          :class="{ selected: selectedRight === item.id, matched: matchedIds.has(item.id), wrong: wrongId === item.id }"
          @click="selectRight(item)"
        >{{ item.chinese }}</div>
      </div>
    </div>

    <!-- 结算界面 -->
    <div v-else class="game-result">
      <h2>游戏结束！</h2>
      <div class="result-stats">
        <div class="rs-item"><span class="rs-label">得分</span><span class="rs-value">{{ score }}</span></div>
        <div class="rs-item"><span class="rs-label">用时</span><span class="rs-value">{{ formatTime(elapsed) }}</span></div>
        <div class="rs-item"><span class="rs-label">正确率</span><span class="rs-value">{{ accuracy }}%</span></div>
      </div>
      <div class="result-actions">
        <el-button type="primary" @click="initGame">再来一局</el-button>
        <el-button @click="emit('done')">退出</el-button>
      </div>

      <!-- 排行榜 -->
      <el-divider />
      <h3 class="leaderboard-title">排行榜</h3>
      <div class="leaderboard">
        <div v-for="(r, i) in leaderboard" :key="r.id" class="lb-row" :class="{ 'lb-me': r.username === savedUsername }">
          <span class="lb-rank">#{{ i + 1 }}</span>
          <span class="lb-name">{{ r.username }}</span>
          <span class="lb-score">{{ r.score }}分</span>
          <span class="lb-acc">{{ r.accuracy }}%</span>
          <span class="lb-time">{{ formatTime(r.time_seconds) }}</span>
        </div>
        <el-empty v-if="!leaderboard.length" description="暂无记录" :image-size="40" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import { vocabApi } from "../api";
import { useUserStore } from "../stores/user";

const props = defineProps({ words: { type: Array, default: () => [] } });
const emit = defineEmits(["done"]);
const store = useUserStore();

const pairs = ref([]);
const leftItems = ref([]);
const rightItems = ref([]);
const matchedIds = ref(new Set());
const selectedLeft = ref(null);
const selectedRight = ref(null);
const wrongId = ref(null);
const score = ref(0);
const correctCount = ref(0);
const elapsed = ref(0);
const leaderboard = ref([]);
const savedUsername = ref("");
let timer = null;

const matchedCount = computed(() => matchedIds.value.size);
const gameOver = computed(() => matchedCount.value === pairs.value.length && pairs.value.length > 0);
const accuracy = computed(() => pairs.value.length ? Math.round(correctCount.value / pairs.value.length * 100) : 0);

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

async function loadLeaderboard() {
  try {
    const { data } = await vocabApi.gameLeaderboard();
    leaderboard.value = data;
  } catch { /* ignore */ }
}

async function initGame() {
  const sample = shuffle(props.words).slice(0, 6);
  pairs.value = sample;
  leftItems.value = shuffle(sample);
  rightItems.value = shuffle(sample);
  matchedIds.value = new Set();
  selectedLeft.value = null;
  selectedRight.value = null;
  wrongId.value = null;
  score.value = 0;
  correctCount.value = 0;
  elapsed.value = 0;
  if (timer) clearInterval(timer);
  timer = setInterval(() => elapsed.value++, 1000);
}

function selectLeft(item) {
  if (matchedIds.value.has(item.id)) return;
  selectedLeft.value = item.id;
  checkMatch();
}

function selectRight(item) {
  if (matchedIds.value.has(item.id)) return;
  selectedRight.value = item.id;
  checkMatch();
}

async function checkMatch() {
  if (!selectedLeft.value || !selectedRight.value) return;
  if (selectedLeft.value === selectedRight.value) {
    matchedIds.value = new Set([...matchedIds.value, selectedLeft.value]);
    score.value += 10;
    correctCount.value++;
  } else {
    wrongId.value = selectedRight.value;
    score.value = Math.max(0, score.value - 2);
    setTimeout(() => { wrongId.value = null; }, 500);
  }
  selectedLeft.value = null;
  selectedRight.value = null;

  // 全部匹配完成，保存成绩
  if (gameOver.value) {
    clearInterval(timer);
    if (store.userId) {
      try {
        await vocabApi.saveGame({
          user_id: store.userId,
          username: store.username,
          score: score.value,
          accuracy: accuracy.value,
          total_pairs: pairs.value.length,
          correct_count: correctCount.value,
          time_seconds: elapsed.value,
        });
        savedUsername.value = store.username;
      } catch { /* ignore */ }
    }
    loadLeaderboard();
  }
}

function formatTime(s) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

onMounted(() => { initGame(); loadLeaderboard(); });
onUnmounted(() => { if (timer) clearInterval(timer); });
</script>

<style scoped>
.game-header { display: flex; justify-content: space-around; margin-bottom: 16px; font-size: 16px; font-weight: 600; }
.game-board { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.column { display: flex; flex-direction: column; gap: 8px; }
.match-card {
  padding: 16px; text-align: center; border: 2px solid #dcdfe6;
  border-radius: 8px; cursor: pointer; transition: all .2s; font-size: 16px;
}
.match-card:hover { border-color: #409eff; }
.match-card.selected { border-color: #409eff; background: #ecf5ff; }
.match-card.matched { border-color: #67c23a; background: #f0f9eb; opacity: 0.6; cursor: default; }
.match-card.wrong { border-color: #f56c6c; background: #fef0f0; animation: shake .3s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }

.game-result { text-align: center; padding: 20px 0; }
.game-result h2 { color: #67c23a; margin-bottom: 16px; font-size: 24px; }
.result-stats { display: flex; justify-content: center; gap: 32px; margin-bottom: 20px; }
.rs-item { text-align: center; }
.rs-label { font-size: 13px; color: #909399; display: block; }
.rs-value { font-size: 28px; font-weight: 700; color: #409eff; }
.result-actions { display: flex; gap: 12px; justify-content: center; margin-bottom: 8px; }

.leaderboard-title { font-size: 16px; color: var(--text-primary); margin-bottom: 12px; }
.leaderboard { max-height: 300px; overflow-y: auto; }
.lb-row {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; border-radius: 6px; margin-bottom: 4px;
  background: #fafafa; font-size: 14px;
}
.lb-row.lb-me { background: #ecf5ff; border: 1px solid #409eff; font-weight: 600; }
.lb-rank { width: 32px; font-weight: 700; color: #e6a23c; flex-shrink: 0; }
.lb-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lb-score { width: 60px; text-align: right; color: #409eff; font-weight: 600; flex-shrink: 0; }
.lb-acc { width: 50px; text-align: right; color: #67c23a; flex-shrink: 0; }
.lb-time { width: 50px; text-align: right; color: #909399; flex-shrink: 0; }

@media (max-width: 480px) {
  .game-board { gap: 12px; }
  .match-card { padding: 12px 8px; font-size: 14px; }
  .result-stats { gap: 16px; }
  .rs-value { font-size: 22px; }
}
</style>
