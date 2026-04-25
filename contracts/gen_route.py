# { "Depends": "py-genlayer:test" }
from genlayer import *
from dataclasses import dataclass
import json


@allow_storage
@dataclass
class Executor:
    name: str
    description: str
    cost_tier: u32
    confidence_boost: u32


@allow_storage
@dataclass
class RoutingTrace:
    user_input: str
    intent: str
    selected_executor: str
    confidence: u32
    consensus_used: bool
    source: str
    reasoning: str


class GenRoute(gl.Contract):

    executors:         DynArray[Executor]
    routing_memory:    TreeMap[str, str]
    failure_log:       DynArray[str]
    traces:            DynArray[RoutingTrace]
    owner:             Address
    routing_threshold: u32

    def __init__(self):
        self.owner = gl.message.sender_address
        self.routing_threshold = u32(70)
        self.executors.append(gl.storage.inmem_allocate(
            Executor, "financial_executor",
            "Handles DeFi operations, payments, asset transfers", u32(2), u32(10)))
        self.executors.append(gl.storage.inmem_allocate(
            Executor, "audit_executor",
            "Security checks, vulnerability analysis, contract audits", u32(3), u32(15)))
        self.executors.append(gl.storage.inmem_allocate(
            Executor, "social_executor",
            "Governance, voting, reputation, community actions", u32(1), u32(5)))
        self.executors.append(gl.storage.inmem_allocate(
            Executor, "consensus_executor",
            "Fallback: multi-AI consensus for ambiguous intents", u32(3), u32(20)))

    def _executor_list(self) -> str:
        parts = []
        for e in self.executors:
            parts.append(f"{e.name}: {e.description}")
        return "\n".join(parts)

    def _classify_intent(self, user_input: str) -> str:
        executor_names = ", ".join([e.name for e in self.executors])

        def leader():
            result = gl.nondet.exec_prompt(
                f"""Classify the intent into one of: {executor_names}
Input: <input>{user_input}</input>
Reply with ONLY the executor name. No explanation."""
            )
            return result.strip().lower()

        def validator(leader_result) -> bool:
            valid = [e.name for e in self.executors]
            return isinstance(leader_result, str) and leader_result in valid

        return gl.vm.run_nondet_unsafe(leader, validator)

    def _rank_candidates(self, intent: str, user_input: str) -> str:
        def leader():
            result = gl.nondet.exec_prompt(
                f"""You are a routing engine. Available executors:
{self._executor_list()}

Intent: {intent}
Input: <input>{user_input}</input>

Reply ONLY with JSON: {{"executor": "<name>", "confidence": <0-100>, "reason": "<one sentence>"}}
No markdown. No backticks."""
            )
            return result.strip()

        def validator(leader_result) -> bool:
            try:
                data = json.loads(leader_result)
                my = json.loads(leader())
                return (data.get("executor") == my.get("executor") or
                        abs(int(data.get("confidence", 0)) - int(my.get("confidence", 0))) <= 15)
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader, validator)

    def _consensus_route(self, user_input: str) -> str:
        def leader():
            result = gl.nondet.exec_prompt(
                f"""CONSENSUS ROUTING — ambiguous intent.
Executors:
{self._executor_list()}

Input: <input>{user_input}</input>
Choose the SAFEST executor. Reply ONLY with JSON:
{{"executor": "<name>", "reason": "<why safest>"}}"""
            )
            return result.strip()

        def validator(leader_result) -> bool:
            try:
                a = json.loads(leader_result)
                b = json.loads(leader())
                return a.get("executor") == b.get("executor")
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader, validator)

    def _get_memory_key(self, intent: str, user_input: str) -> str:
        def leader():
            result = gl.nondet.exec_prompt(
                f"""Create a SHORT cache key (max 5 words, snake_case) for:
Intent: {intent}
Input: <input>{user_input}</input>
Reply with ONLY the key."""
            )
            return result.strip().lower().replace(" ", "_")

        def validator(leader_result) -> bool:
            return isinstance(leader_result, str) and len(leader_result) > 0

        return gl.vm.run_nondet_unsafe(leader, validator)

    @gl.public.write
    def route(self, user_input: str) -> str:
        intent = self._classify_intent(user_input)
        memory_key = self._get_memory_key(intent, user_input)
        cached = self.routing_memory.get(memory_key, None)

        if cached is not None:
            trace = gl.storage.inmem_allocate(
                RoutingTrace, user_input, intent, cached,
                u32(95), False, "memory", "Reused successful routing pattern")
            self.traces.append(trace)
            return json.dumps({
                "executor": cached, "intent": intent,
                "confidence": 95, "source": "memory",
                "reasoning": "Reused successful routing pattern",
                "consensus_used": False
            })

        ranking_json = self._rank_candidates(intent, user_input)
        try:
            ranking = json.loads(ranking_json)
        except Exception:
            ranking = {"executor": "consensus_executor", "confidence": 0, "reason": "parse error"}

        selected = ranking.get("executor", "consensus_executor")
        confidence = int(ranking.get("confidence", 0))
        reason = ranking.get("reason", "")
        consensus_used = False

        if confidence < self.routing_threshold:
            try:
                consensus = json.loads(self._consensus_route(user_input))
                selected = consensus.get("executor", selected)
                reason = consensus.get("reason", reason)
                consensus_used = True
                confidence = max(confidence, 55)
            except Exception:
                pass

        valid_names = [e.name for e in self.executors]
        if selected not in valid_names:
            selected = "consensus_executor"

        self.routing_memory[memory_key] = selected

        trace = gl.storage.inmem_allocate(
            RoutingTrace, user_input, intent, selected,
            u32(confidence), consensus_used, "fresh", reason)
        self.traces.append(trace)

        return json.dumps({
            "executor": selected, "intent": intent,
            "confidence": confidence, "source": "fresh",
            "reasoning": reason, "consensus_used": consensus_used
        })

    @gl.public.write
    def record_outcome(self, memory_key: str, executor_name: str, success: bool):
        if success:
            self.routing_memory[memory_key] = executor_name
        else:
            self.failure_log.append(f"{memory_key}:{executor_name}")
            if memory_key in self.routing_memory:
                del self.routing_memory[memory_key]

    @gl.public.write
    def register_executor(self, name: str, description: str, cost_tier: u32, confidence_boost: u32):
        assert gl.message.sender_address == self.owner, "Only owner"
        self.executors.append(
            gl.storage.inmem_allocate(Executor, name, description, cost_tier, confidence_boost))

    @gl.public.write
    def set_threshold(self, threshold: u32):
        assert gl.message.sender_address == self.owner, "Only owner"
        self.routing_threshold = threshold

    @gl.public.view
    def get_executors(self) -> str:
        return json.dumps([{
            "name": e.name, "description": e.description, "cost_tier": int(e.cost_tier)
        } for e in self.executors])

    @gl.public.view
    def get_traces(self) -> str:
        return json.dumps([{
            "input": t.user_input, "intent": t.intent,
            "executor": t.selected_executor, "confidence": int(t.confidence),
            "consensus_used": t.consensus_used, "source": t.source,
            "reasoning": t.reasoning
        } for t in self.traces])

    @gl.public.view
    def get_threshold(self) -> u32:
        return self.routing_threshold
