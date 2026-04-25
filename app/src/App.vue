<template>
  <main class="main">
    <div class="container">

      <header class="hero">
        <div class="eyebrow">GenLayer · Intelligent Contract</div>
        <h1>GenRoute</h1>
        <p>AI decides the execution path — not just the outcome.</p>
      </header>

      <section class="card">
        <label>What do you want to do?</label>
        <textarea
          v-model="userInput"
          rows="3"
          placeholder="Describe your task, intent, or transaction…"
        />

        <div class="examples">
          <button
            v-for="ex in examples"
            :key="ex"
            class="pill"
            @click="userInput = ex"
          >{{ ex }}</button>
        </div>

        <button class="route-btn" :disabled="loading || !userInput.trim()" @click="handleRoute">
          {{ loading ? 'Routing…' : 'Route Intent →' }}
        </button>
      </section>

      <div v-if="error" class="card error-card">{{ error }}</div>

      <section v-if="result" class="card result-card">
        <div class="result-header">
          <span class="label-muted">Routing Decision</span>
          <span v-if="result.source === 'memory'" class="badge memory">⚡ From Memory</span>
          <span v-if="result.consensus_used" class="badge consensus">⚖️ Consensus Triggered</span>
        </div>

        <div class="grid">
          <div>
            <div class="item-label">Intent</div>
            <div class="item-value">{{ result.intent?.replace('_executor','').toUpperCase() }}</div>
          </div>
          <div>
            <div class="item-label">Executor</div>
            <ExecutorBadge :name="result.executor" />
          </div>
          <div class="full">
            <div class="item-label">Confidence</div>
            <ConfidenceBar :value="result.confidence" />
          </div>
          <div class="full">
            <div class="item-label">Reasoning</div>
            <div class="reasoning">{{ result.reasoning }}</div>
          </div>
        </div>

        <div class="trace-flow">
          <template v-for="(step, i) in traceSteps" :key="step">
            <span class="step">{{ step }}</span>
            <span v-if="i < traceSteps.length - 1" class="arrow">→</span>
          </template>
        </div>
      </section>

      <section v-if="traces.length" class="card">
        <h2>Routing History ({{ traces.length }})</h2>
        <div v-for="(t, i) in traces.slice().reverse().slice(0,5)" :key="i" class="trace-row">
          <span class="trace-input">{{ t.input }}</span>
          <ExecutorBadge :name="t.executor" />
          <span class="conf">{{ t.confidence }}%</span>
          <span>{{ t.source === 'memory' ? '⚡' : '🔄' }}</span>
        </div>
      </section>

    </div>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createClient } from '@genlayer/js'
import ExecutorBadge from './components/ExecutorBadge.vue'
import ConfidenceBar from './components/ConfidenceBar.vue'

const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS
const client = createClient({ network: import.meta.env.VITE_GENLAYER_NETWORK || 'testnet' })

const userInput = ref('')
const loading = ref(false)
const result = ref(null)
const traces = ref([])
const error = ref(null)

const examples = [
  'Check this Solidity contract for reentrancy vulnerabilities',
  'Swap 0.5 ETH for USDC on Uniswap',
  'Vote YES on governance proposal #17',
  'Stake 100 GEN tokens into the validator pool',
]

const traceSteps = computed(() => {
  if (!result.value) return []
  const steps = ['Input', 'Classifier', 'Ranker']
  if (result.value.consensus_used) steps.push('Consensus')
  steps.push('Executor', 'Onchain Log')
  return steps
})

async function handleRoute() {
  if (!userInput.value.trim()) return
  loading.value = true
  error.value = null
  result.value = null

  try {
    const txHash = await client.writeContract({
      address: CONTRACT_ADDRESS,
      functionName: 'route',
      args: [userInput.value],
    })
    const receipt = await client.waitForTransactionReceipt({ hash: txHash })
    result.value = JSON.parse(receipt.result ?? '{}')

    const schema = await client.getContractSchema(CONTRACT_ADDRESS)
    const contract = client.readContract({ address: CONTRACT_ADDRESS, abi: schema })
    const raw = await contract.read.get_traces()
    traces.value = JSON.parse(raw)
  } catch (err) {
    error.value = err?.message ?? 'Unknown error'
  } finally {
    loading.value = false
  }
}
</script>

<style>
:root {
  --bg: #0a0a0f;
  --surface: #12121a;
  --surface2: #1a1a28;
  --border: #2a2a40;
  --text: #e8e8f0;
  --muted: #7a7a9a;
  --accent: #6c63ff;
  --accent2: #a78bfa;
  --r: 12px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; }
.main { min-height: 100vh; padding: 2rem 1rem 4rem; }
.container { max-width: 760px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.25rem; }
.hero { text-align: center; padding: 2rem 0 1rem; }
.eyebrow { font-size: .75rem; letter-spacing: .15em; text-transform: uppercase; color: var(--accent2); margin-bottom: .5rem; }
h1 { font-size: clamp(2.5rem,8vw,4rem); font-weight: 800; background: linear-gradient(135deg,#fff 30%,var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero p { color: var(--muted); margin-top: .5rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 1.5rem; }
label { font-size: .85rem; color: var(--muted); display: block; margin-bottom: .5rem; }
textarea { width: 100%; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 1rem; padding: .75rem 1rem; resize: vertical; outline: none; }
textarea:focus { border-color: var(--accent); }
.examples { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .75rem; }
.pill { background: var(--surface2); border: 1px solid var(--border); border-radius: 999px; color: var(--muted); font-size: .75rem; padding: .25rem .75rem; cursor: pointer; }
.pill:hover { border-color: var(--accent2); color: var(--text); }
.route-btn { margin-top: 1rem; width: 100%; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; padding: .875rem; cursor: pointer; }
.route-btn:disabled { opacity: .4; cursor: not-allowed; }
.error-card { border-color: #7f1d1d; background: #1a0a0a; color: #f87171; }
.result-header { display: flex; align-items: center; gap: .5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.label-muted { font-size: .8rem; color: var(--muted); text-transform: uppercase; letter-spacing: .1em; }
.badge { border-radius: 999px; font-size: .7rem; padding: .15rem .5rem; }
.badge.memory { background: #0f3a0f; color: #4ade80; border: 1px solid #166534; }
.badge.consensus { background: #3a2a00; color: #fbbf24; border: 1px solid #92400e; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.full { grid-column: 1 / -1; }
.item-label { font-size: .75rem; color: var(--muted); margin-bottom: .25rem; }
.item-value { font-weight: 700; font-size: 1.1rem; }
.reasoning { color: var(--muted); font-size: .9rem; font-style: italic; }
.trace-flow { display: flex; align-items: center; flex-wrap: wrap; gap: .25rem; padding-top: 1rem; margin-top: 1.25rem; border-top: 1px solid var(--border); }
.step { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; font-size: .72rem; padding: .2rem .5rem; color: var(--muted); }
.arrow { color: var(--accent2); font-size: .75rem; }
h2 { font-size: 1rem; font-weight: 700; margin-bottom: 1rem; }
.trace-row { display: flex; align-items: center; gap: .5rem; padding: .6rem .75rem; background: var(--surface2); border-radius: 8px; margin-bottom: .5rem; flex-wrap: wrap; }
.trace-input { flex: 1; font-size: .85rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conf { font-size: .8rem; color: var(--muted); }
</style>
