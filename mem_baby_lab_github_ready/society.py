from __future__ import annotations
from dataclasses import dataclass, asdict
from affect_space import AffectState, clamp, mean_state

@dataclass
class SocietyField:
    coherence_bias: float
    resource_pressure: float
    conformity_pressure: float
    instability_cap: float
    diversity_support: float

    def apply(self, state: AffectState, group_states: list[AffectState]) -> AffectState:
        group_mean = mean_state(group_states)
        state.coherence = clamp(
            state.coherence
            + (self.coherence_bias - 0.5) * 0.08
            + (group_mean.coherence - state.coherence) * self.conformity_pressure * 0.10
        )
        state.arousal = clamp(state.arousal - self.resource_pressure * 0.04)
        state.approach = clamp(state.approach - self.resource_pressure * 0.02)
        state.valence = clamp(state.valence + (state.valence - group_mean.valence) * self.diversity_support * 0.05)
        if state.stability < (1.0 - self.instability_cap):
            state.stability = clamp(state.stability + 0.05)
        return state

    def as_dict(self) -> dict:
        return asdict(self)
