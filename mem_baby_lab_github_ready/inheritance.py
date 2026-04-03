from __future__ import annotations
from dataclasses import dataclass
import random
from affect_space import AffectState, blend, clamp

@dataclass
class ChildGenome:
    state: AffectState
    traits: dict

def mix_traits(a: dict, b: dict, rng: random.Random, mutation_strength: float) -> dict:
    child = {}
    for key in sorted(set(a.keys()) | set(b.keys())):
        av = float(a.get(key, 0.5))
        bv = float(b.get(key, 0.5))
        roll = rng.random()
        if roll < 0.45:
            inherited = av
        elif roll < 0.90:
            inherited = bv
        else:
            inherited = (av + bv) / 2.0
        inherited += rng.uniform(-mutation_strength, mutation_strength)
        child[key] = clamp(inherited)
    return child

def derive_child(parent_a: dict, parent_b: dict, rng: random.Random, mutation_strength: float) -> ChildGenome:
    base_state = blend(parent_a["state"], parent_b["state"], 0.5)
    base_state.valence += rng.uniform(-mutation_strength, mutation_strength)
    base_state.arousal += rng.uniform(-mutation_strength, mutation_strength)
    base_state.coherence += rng.uniform(-mutation_strength, mutation_strength)
    base_state.approach += rng.uniform(-mutation_strength, mutation_strength)
    base_state.stability += rng.uniform(-mutation_strength, mutation_strength)
    base_state.clip()
    traits = mix_traits(parent_a["traits"], parent_b["traits"], rng, mutation_strength)
    return ChildGenome(state=base_state, traits=traits)
