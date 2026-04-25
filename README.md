[README.md](https://github.com/user-attachments/files/27086715/README.md)
# Genroute-dop# GenRoute

**AI execution routing as a first-class blockchain primitive.**

GenRoute is an Intelligent Contract built on [GenLayer](https://genlayer.com) that routes user intents to the optimal execution path using AI-driven classification, consensus-aware ranking, and adaptive memory.

Instead of executing logic directly, the contract first asks: *which executor should handle this?*

---

## Why GenRoute

Traditional smart contracts are deterministic. They execute predefined paths. They cannot adapt.

Real-world intent is ambiguous. The hardest problem in decentralised systems is often not *what* to execute — it is *how to choose* before execution begins.

GenRoute solves this by introducing **execution routing as a first-class primitive**.

---

## Core Flow

```
User Intent
   ↓
Intent Classifier (GenLayer AI consensus)
   ↓
Memory Check — was this intent routed before?
   ├─ HIT  → Cached Executor (instant, 95% confidence)
   └─ MISS → Routing Ranker (AI ranks candidates)
                ↓
             Confidence Check
             ├─ HIGH (≥ threshold) → Selected Executor
             └─ LOW               → Consensus Router (multi-AI fallback)
                                       ↓
                                    Executor
                                       ↓
                                    Onchain Trace
                                    ├─ intent
                                    ├─ candidates
                                    ├─ selected executor
                                    ├─ confidence score
                                    ├─ consensus_used flag
                                    ├─ source (fresh | memory)
                                    └─ reasoning
```

---

## Executor Registry

| Executor | Domain | Cost Tier |
|---|---|---|
| `financial_executor` | DeFi, payments, asset transfers | Medium |
| `audit_executor` | Security, vulnerability analysis | Premium |
| `social_executor` | Governance, voting, reputation | Low |
| `consensus_executor` | Ambiguous / fallback (multi-AI) | Premium |

New executors can be registered by the contract owner via `register_executor()`.

---

## Adaptive Memory

GenRoute builds an onchain memory of successful routing decisions.

- First request for a pattern → full AI pipeline
- Subsequent similar requests → instant cache hit (95% confidence)
- Failed routes → removed from memory, next call goes fresh

This makes the system progressively faster and cheaper — **the contract learns**.

---

## Why GenLayer

GenRoute is only possible on GenLayer because:

- Non-deterministic AI classification is part of consensus, not external
- Routing decisions are verifiable and replayable onchain
- The Equivalence Principle allows validators to agree on subjective intent classifications
- Python-native development enables complex routing logic without Solidity constraints

---

## Project Structure

```
genroute/
├── contracts/
│   └── gen_route.py          # Intelligent Contract (GenLayer Python)
├── tests/
│   └── test_gen_route.py     # Integration tests (genvm-test)
├── scripts/
│   └── deploy.ts             # Deploy script (GenLayer JS)
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx       # Main UI
    │   │   └── globals.css
    │   └── lib/
    │       └── types.ts
    ├── package.json
    └── next.config.js
```

---

## Setup & Deploy

### 1. Install GenLayer CLI

```bash
npm install -g @genlayer/cli
genlayer init
genlayer up
```

### 2. Deploy the contract

```bash
genlayer deploy --contract contracts/gen_route.py
```

Or use the deploy script:

```bash
cd frontend
npm install
npx genlayer deploy scripts/deploy.ts
```

Copy the printed contract address into `frontend/.env.local`:

```
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...
```

### 3. Run the frontend

```bash
cd frontend
npm run dev
```

### 4. Run tests

```bash
pip install genlayer-test
pytest tests/ -v
```

---

## Contract API

### Write Methods

| Method | Args | Description |
|---|---|---|
| `route(user_input)` | `str` | Classify, rank, and route the intent. Returns JSON. |
| `record_outcome(key, executor, success)` | `str, str, bool` | Reinforce or penalise a cached route. |
| `register_executor(name, desc, cost, boost)` | `str, str, int, int` | Add a new executor (owner only). |
| `set_threshold(threshold)` | `int` | Set confidence threshold 0–100 (owner only). |

### View Methods

| Method | Returns | Description |
|---|---|---|
| `get_executors()` | `str` (JSON) | List all registered executors. |
| `get_traces()` | `str` (JSON) | Full routing history log. |
| `get_threshold()` | `int` | Current confidence threshold. |

### `route()` Response

```json
{
  "executor": "audit_executor",
  "intent": "audit_executor",
  "confidence": 82,
  "source": "fresh",
  "reasoning": "Input involves vulnerability analysis of on-chain code.",
  "consensus_used": false
}
```

---

## Future Extensions

- **Executor marketplace** — pay to register premium executors; routing fees distributed to executor providers
- **Reputation scoring** — executors gain/lose reputation based on outcome feedback
- **Policy-based routing** — DAO-governed routing rules for enterprise deployments
- **MEV-aware routing** — detect and reroute transactions at risk of front-running
- **Multi-agent orchestration** — chain executor calls for complex multi-step workflows

---

## One-liner

> GenRoute turns smart contracts into adaptive decision systems — where AI selects the execution path before the contract acts.

---

## License

MIT
