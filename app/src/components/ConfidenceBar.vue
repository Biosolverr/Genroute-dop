<template>
  <div class="wrap">
    <div class="track">
      <div class="fill" :style="{ width: value + '%', background: color }" />
    </div>
    <span :style="{ color }">{{ value }}%</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ value: Number })
const color = computed(() => props.value >= 70 ? '#22c55e' : props.value >= 40 ? '#f59e0b' : '#ef4444')
</script>

<style scoped>
.wrap { display: flex; align-items: center; gap: .75rem; font-weight: 600; font-size: .9rem; }
.track { flex: 1; height: 6px; background: #1a1a28; border-radius: 999px; overflow: hidden; }
.fill { height: 100%; border-radius: 999px; transition: width .5s; }
</style>
