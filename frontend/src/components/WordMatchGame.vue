<template>
  <div class="match-game">
    <div class="game-header">
      <span>用时: {{ formatTime(elapsed) }}</span>
      <span>得分: {{ score }}</span>
      <span>剩余: {{ pairs.length - matchedCount }}</span>
    </div>
    <div v-if="!gameOver" class="game-board">
      <div class="column">
        <div v-for="item in leftItems" :key="item.id" class="match-card" :class="{ selected: selectedLeft === item.id, matched: matchedIds.has(item.id), wrong: wrongId === item.id }" @click="selectLeft(item)">
          {{ item.english }}
        </div>
      </div>
      <div class="column">
        <div v-for="item in rightItems" :key="item.id" class="match-card" :class="{ selected: selectedRight === item.id, matched: matchedIds.has(item.id), wrong: wrongId === item.id }" @click="selectRight(item)">
          {{ item.chinese }}
        </div>
      </div>
    </div>
    <div v-else class="game-result">
      <h2>游戏结束！</h2>
      <p>用时 {{ formatTime(elapsed) }}，得分 {{ score }}，正确率 {{ Math.round(correctCount / pairs.length * 100) }}%</p>
      <el-button type="primary" @click="initGame">再来一局</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({ words: { type: Array, default: () => [] } });
const emit = defineEmits(["done"]);

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
let timer = null;

const matchedCount = computed(() => matchedIds.value.size);
const gameOver = computed(() => matchedCount.value === pairs.value.length && pairs.value.length > 0);

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function initGame() {
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

function checkMatch() {
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
}

function formatTime(s) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

onMounted(initGame);
onUnmounted(() => { if (timer) clearInterval(timer); });
</script>

<style scoped>
.game-header { display: flex; justify-content: space-around; margin-bottom: 16px; font-size: 16px; font-weight: 600; }
.game-board { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.column { display: flex; flex-direction: column; gap: 8px; }
.match-card { padding: 16px; text-align: center; border: 2px solid #dcdfe6; border-radius: 8px; cursor: pointer; transition: all .2s; font-size: 16px; }
.match-card:hover { border-color: #409eff; }
.match-card.selected { border-color: #409eff; background: #ecf5ff; }
.match-card.matched { border-color: #67c23a; background: #f0f9eb; opacity: 0.6; cursor: default; }
.match-card.wrong { border-color: #f56c6c; background: #fef0f0; animation: shake .3s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
.game-result { text-align: center; padding: 40px; }
.game-result h2 { color: #67c23a; margin-bottom: 12px; }
</style>
