<template>
  <span class="executor-badge" :style="{ borderColor: meta.color, color: meta.color }">
    {{ meta.icon }} {{ meta.label }}
  </span>
</template>

<script setup>
const props = defineProps({ name: String })

const MAP = {
  financial_executor: { label: 'Financial',          color: '#22c55e', icon: '💰' },
  audit_executor:     { label: 'Security Audit',     color: '#ef4444', icon: '🔐' },
  social_executor:    { label: 'Governance',          color: '#8b5cf6', icon: '🗳️' },
  consensus_executor: { label: 'Consensus (Multi-AI)',color: '#f59e0b', icon: '⚖️' },
}

const meta = MAP[props.name] ?? { label: props.name, color: '#6b7280', icon: '🔄' }
</script>

<style scoped>
.executor-badge {
  display: inline-flex; align-items: center; gap: .35rem;
  border: 1px solid; border-radius: 999px;
  font-size: .8rem; font-weight: 600; padding: .2rem .65rem;
}
</style>
