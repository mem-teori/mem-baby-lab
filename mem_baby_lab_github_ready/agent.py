from __future__ import annotations
from dataclasses import dataclass, field
import random, statistics
from affect_space import AffectState, clamp, distance

@dataclass
class MemoryRecord:
    step: int
    state: AffectState
    stability_score: float
    collapse_risk: float
    energy: float
    plasticity: float
    transition_score: float

@dataclass
class Agent:
    agent_id: str
    lineage: str
    state: AffectState
    traits: dict
    memory: list[MemoryRecord] = field(default_factory=list)
    collapsed: bool = False
    collapse_type: str | None = None
    survival_profile: str | None = None
    energy: float = 1.0
    plasticity: float = 0.5

    def perceive_stimulus(self, rng: random.Random, strength: float) -> dict:
        return {
            "valence_shift": rng.uniform(-strength, strength),
            "arousal_shift": rng.uniform(-strength, strength),
            "coherence_shift": rng.uniform(-strength, strength),
            "approach_shift": rng.uniform(-strength, strength),
        }

    def update(self, step, stimulus, group_mean, rng, drift_strength, interaction_strength,
               energy_drain_rate, plasticity_cost_weight, recovery_rate,
               recovery_coherence_threshold, recovery_arousal_ceiling,
               plasticity_window, plasticity_floor, plasticity_ceiling):
        if self.collapsed:
            return
        sensitivity = self.traits.get("sensitivity", 0.5)
        exploration = self.traits.get("exploration_bias", 0.5)
        coherence_need = self.traits.get("coherence_need", 0.5)
        learning_rate = self.traits.get("learning_rate", 0.5)

        self.state.valence = clamp(self.state.valence + stimulus["valence_shift"] * sensitivity + (group_mean.valence - self.state.valence) * interaction_strength * 0.25)
        self.state.arousal = clamp(self.state.arousal + stimulus["arousal_shift"] * (0.6 + sensitivity * 0.4) + (exploration - 0.5) * drift_strength)
        self.state.coherence = clamp(self.state.coherence + stimulus["coherence_shift"] * (1.0 - coherence_need * 0.4) + (coherence_need - 0.5) * 0.05)
        self.state.approach = clamp(self.state.approach + stimulus["approach_shift"] * 0.7 + (exploration - 0.5) * 0.05)

        if self.memory:
            recent = self.memory[-plasticity_window:]
            trans = [m.transition_score for m in recent]
            recent_variance = statistics.pstdev(trans) if len(trans) > 1 else 0.0
        else:
            recent_variance = 0.0

        arousal_drive = abs(self.state.arousal - 0.5) * 0.35
        learning_drive = learning_rate * 0.35
        exploration_drive = abs(exploration - 0.5) * 0.20
        variance_drive = min(1.0, recent_variance * 3.0) * 0.10
        self.plasticity = clamp(arousal_drive + learning_drive + exploration_drive + variance_drive, plasticity_floor, plasticity_ceiling)

        energy_cost = energy_drain_rate + max(0.0, self.state.coherence - 0.7) * 0.05 + self.plasticity * plasticity_cost_weight
        self.energy = clamp(self.energy - energy_cost)
        if self.plasticity < 0.30:
            self.energy = clamp(self.energy + 0.01)
        if self.state.coherence >= recovery_coherence_threshold and self.state.arousal <= recovery_arousal_ceiling:
            self.energy = clamp(self.energy + recovery_rate)

        arousal_penalty = abs(self.state.arousal - 0.55)
        coherence_gain = 0.55 * self.state.coherence + 0.20 * self.state.valence + 0.15 * (1.0 - arousal_penalty) + 0.10 * self.energy
        plasticity_cost = self.plasticity * 0.30
        energy_penalty = (1.0 - self.energy) * 0.25
        adaptive_bonus = max(0.0, 0.18 - abs(self.plasticity - 0.45)) * 0.35
        rigid_bonus = max(0.0, 0.28 - self.plasticity) * max(0.0, 0.45 - learning_rate) * 1.20
        shock_penalty = 0.10 if self.plasticity < 0.30 and abs(self.state.arousal - 0.5) > 0.22 else 0.0
        target_stability = clamp(coherence_gain - plasticity_cost - energy_penalty + adaptive_bonus + rigid_bonus - shock_penalty)

        self.state.stability = clamp(self.state.stability + (target_stability - self.state.stability) * (0.14 + learning_rate * 0.10))

    def compute_metrics(self, collapse_window=10):
        if not self.memory:
            transition = 0.0
        else:
            transition = distance(self.state, self.memory[-1].state)
        stability_score = 0.40 * self.state.stability + 0.25 * self.state.coherence + 0.10 * self.state.valence + 0.10 * self.energy + 0.15 * (1.0 - abs(self.state.arousal - 0.55))
        collapse_risk = clamp(1.0 - stability_score + (1.0 - self.energy) * 0.12)
        if self.memory:
            recent = self.memory[-collapse_window:]
            vals = [m.stability_score for m in recent] + [stability_score]
            stability_variance = statistics.pstdev(vals) if len(vals) > 1 else 0.0
            stability_trend = vals[-1] - vals[0]
        else:
            stability_variance = 0.0
            stability_trend = 0.0
        return {
            "stability_score": round(stability_score, 4),
            "transition_score": round(transition, 4),
            "collapse_risk": round(collapse_risk, 4),
            "energy": round(self.energy, 4),
            "plasticity": round(self.plasticity, 4),
            "stability_variance": round(stability_variance, 4),
            "stability_trend": round(stability_trend, 4),
        }

    def classify_collapse(self, metrics):
        variance = metrics["stability_variance"]
        trend = metrics["stability_trend"]
        if variance >= 0.05 and abs(trend) < 0.10:
            return "oscillation"
        if variance < 0.03 and trend <= -0.18:
            return "catastrophic"
        if variance < 0.05 and trend < -0.06:
            return "erosion"
        return "marginal"

    def _classify_survival(self):
        if not self.memory:
            return "unknown"
        mean_stability = statistics.mean(m.stability_score for m in self.memory)
        mean_plasticity = statistics.mean(m.plasticity for m in self.memory)
        learning_rate = self.traits.get("learning_rate", 0.5)
        transition_var = statistics.pstdev(m.transition_score for m in self.memory) if len(self.memory) > 1 else 0.0
        if mean_stability >= 0.50 and mean_plasticity < 0.28 and learning_rate < 0.45:
            return "rigid"
        if mean_stability >= 0.48 and 0.30 <= mean_plasticity <= 0.60:
            return "adaptive"
        if transition_var >= 0.06 and mean_stability < 0.55:
            return "oscillatory"
        return "marginal"

    def remember(self, step, metrics, max_memory=25):
        self.memory.append(MemoryRecord(
            step=step,
            state=AffectState(**self.state.as_dict()),
            stability_score=metrics["stability_score"],
            collapse_risk=metrics["collapse_risk"],
            energy=metrics["energy"],
            plasticity=metrics["plasticity"],
            transition_score=metrics["transition_score"],
        ))
        if len(self.memory) > max_memory:
            self.memory = self.memory[-max_memory:]

    def finalize_profile(self):
        if not self.collapsed:
            self.survival_profile = self._classify_survival()

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "lineage": self.lineage,
            "collapsed": self.collapsed,
            "collapse_type": self.collapse_type,
            "survival_profile": self.survival_profile,
            "energy": round(self.energy, 4),
            "plasticity": round(self.plasticity, 4),
            "state": self.state.as_dict(),
            "traits": self.traits,
        }
