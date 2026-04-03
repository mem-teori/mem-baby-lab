from affect_space import AffectState

PARENT_PAIRS = {
    "pair_1_expansion_vs_stability": {
        "parent_a": {
            "name": "expansion",
            "state": AffectState(0.72, 0.80, 0.40, 0.84, 0.36),
            "traits": {"exploration_bias": 0.82, "coherence_need": 0.30, "learning_rate": 0.66, "sensitivity": 0.48},
        },
        "parent_b": {
            "name": "stability",
            "state": AffectState(0.64, 0.36, 0.82, 0.48, 0.86),
            "traits": {"exploration_bias": 0.25, "coherence_need": 0.86, "learning_rate": 0.32, "sensitivity": 0.58},
        },
    },
    "pair_2_sensitive_vs_robust": {
        "parent_a": {
            "name": "sensitive",
            "state": AffectState(0.58, 0.72, 0.52, 0.46, 0.40),
            "traits": {"exploration_bias": 0.52, "coherence_need": 0.64, "learning_rate": 0.54, "sensitivity": 0.88},
        },
        "parent_b": {
            "name": "robust",
            "state": AffectState(0.60, 0.46, 0.62, 0.52, 0.78),
            "traits": {"exploration_bias": 0.44, "coherence_need": 0.58, "learning_rate": 0.38, "sensitivity": 0.20},
        },
    },
    "pair_3_fast_vs_slow_learning": {
        "parent_a": {
            "name": "fast_learning",
            "state": AffectState(0.62, 0.68, 0.46, 0.56, 0.40),
            "traits": {"exploration_bias": 0.60, "coherence_need": 0.42, "learning_rate": 0.92, "sensitivity": 0.50},
        },
        "parent_b": {
            "name": "slow_learning",
            "state": AffectState(0.56, 0.34, 0.72, 0.44, 0.82),
            "traits": {"exploration_bias": 0.34, "coherence_need": 0.72, "learning_rate": 0.18, "sensitivity": 0.44},
        },
    },
}
