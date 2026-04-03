from __future__ import annotations
from dataclasses import dataclass

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

@dataclass
class AffectState:
    valence: float
    arousal: float
    coherence: float
    approach: float
    stability: float

    def clip(self) -> None:
        self.valence = clamp(self.valence)
        self.arousal = clamp(self.arousal)
        self.coherence = clamp(self.coherence)
        self.approach = clamp(self.approach)
        self.stability = clamp(self.stability)

    def as_dict(self) -> dict:
        return {
            "valence": round(self.valence, 4),
            "arousal": round(self.arousal, 4),
            "coherence": round(self.coherence, 4),
            "approach": round(self.approach, 4),
            "stability": round(self.stability, 4),
        }

def blend(a: AffectState, b: AffectState, weight: float = 0.5) -> AffectState:
    inv = 1.0 - weight
    return AffectState(
        valence=a.valence * inv + b.valence * weight,
        arousal=a.arousal * inv + b.arousal * weight,
        coherence=a.coherence * inv + b.coherence * weight,
        approach=a.approach * inv + b.approach * weight,
        stability=a.stability * inv + b.stability * weight,
    )

def distance(a: AffectState, b: AffectState) -> float:
    return (
        abs(a.valence - b.valence)
        + abs(a.arousal - b.arousal)
        + abs(a.coherence - b.coherence)
        + abs(a.approach - b.approach)
        + abs(a.stability - b.stability)
    ) / 5.0

def mean_state(states: list[AffectState]) -> AffectState:
    n = max(1, len(states))
    return AffectState(
        valence=sum(s.valence for s in states) / n,
        arousal=sum(s.arousal for s in states) / n,
        coherence=sum(s.coherence for s in states) / n,
        approach=sum(s.approach for s in states) / n,
        stability=sum(s.stability for s in states) / n,
    )
