from dataclasses import dataclass

@dataclass
class SimulationConfig:
    steps: int = 120
    seed: int = 42
    mutation_strength: float = 0.08
    drift_strength: float = 0.05
    stimulus_strength: float = 0.18
    interaction_strength: float = 0.10
    collapse_threshold: float = 0.18
    high_instability_threshold: float = 0.82
    run_with_society: bool = True
    output_dir: str = "outputs"
    energy_drain_rate: float = 0.014
    plasticity_cost_weight: float = 0.07
    recovery_rate: float = 0.045
    recovery_coherence_threshold: float = 0.74
    recovery_arousal_ceiling: float = 0.46
    plasticity_window: int = 8
    collapse_window: int = 10
    plasticity_floor: float = 0.05
    plasticity_ceiling: float = 0.95

@dataclass
class SocietyConfig:
    coherence_bias: float = 0.58
    resource_pressure: float = 0.30
    conformity_pressure: float = 0.22
    instability_cap: float = 0.85
    diversity_support: float = 0.18
