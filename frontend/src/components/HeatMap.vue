<template>
  <div class="heatmap-container">
    <div class="heatmap-grid">
      <div v-for="(cell, i) in cells" :key="i" class="heatmap-cell" :style="{ background: cell.color }" :title="cell.label" />
    </div>
    <div class="heatmap-legend">
      <span>少</span>
      <div v-for="c in legendColors" :key="c" class="heatmap-cell small" :style="{ background: c }" />
      <span>多</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{date, count}]
  weeks: { type: Number, default: 12 },
});

const colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"];

function getColor(count) {
  if (count === 0) return colors[0];
  if (count <= 3) return colors[1];
  if (count <= 6) return colors[2];
  if (count <= 10) return colors[3];
  return colors[4];
}

const legendColors = computed(() => colors);

const cells = computed(() => {
  const map = {};
  props.data.forEach((d) => { map[d.date] = d.count; });
  const result = [];
  const today = new Date();
  const totalDays = props.weeks * 7;
  for (let i = totalDays - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const count = map[key] || 0;
    result.push({ date: key, count, color: getColor(count), label: `${key}: ${count}次` });
  }
  return result;
});
</script>

<style scoped>
.heatmap-grid { display: grid; grid-template-columns: repeat(v-bind('weeks'), 1fr); gap: 2px; }
.heatmap-cell { width: 14px; height: 14px; border-radius: 2px; }
.heatmap-cell.small { width: 12px; height: 12px; }
.heatmap-legend { display: flex; align-items: center; gap: 4px; margin-top: 8px; font-size: 12px; color: #909399; }
</style>
