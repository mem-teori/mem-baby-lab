from __future__ import annotations
import copy, json, os, random, statistics
from config import SimulationConfig, SocietyConfig
from profiles import PARENT_PAIRS
from inheritance import derive_child
from agent import Agent
from affect_space import mean_state, AffectState
from society import SocietyField

def _seed_population_from_pairs(cfg, rng, children_per_pair=2):
    population = []
    for lineage, pair in PARENT_PAIRS.items():
        for i in range(children_per_pair):
            genome = derive_child(pair["parent_a"], pair["parent_b"], rng, cfg.mutation_strength)
            population.append(Agent(agent_id=f"g0_{lineage}_{i+1}", lineage=lineage, state=genome.state, traits=genome.traits))
    return population

def _score_agent(agent):
    s = agent["state"]
    profile_bonus = {"adaptive":0.10, "rigid":0.04, "marginal":-0.02, "oscillatory":-0.06, None:0.0}.get(agent.get("survival_profile"),0.0)
    base = 0.38*float(s["stability"]) + 0.22*float(s["coherence"]) + 0.10*float(s["valence"]) + 0.20*float(agent.get("energy",0.0)) + profile_bonus
    if agent.get("collapsed"):
        base -= 0.20
    return round(base, 6)

def _pick_parents(final_agents, rng, n_pairs):
    scored = [dict(a, fitness=_score_agent(a)) for a in final_agents]
    scored.sort(key=lambda x: x["fitness"], reverse=True)
    living = [a for a in scored if not a["collapsed"]]
    pool = living if len(living) >= 2 else scored
    choices = pool
    weights = [max(0.01, a["fitness"] + 0.35) for a in choices]
    parent_pairs = []
    while len(parent_pairs) < n_pairs:
        pa = rng.choices(choices, weights=weights, k=1)[0]
        pb = rng.choices(choices, weights=weights, k=1)[0]
        if pa["agent_id"] != pb["agent_id"]:
            parent_pairs.append((pa, pb))
    return parent_pairs

def _agent_dict_to_parent(agent):
    return {"name": agent["agent_id"], "state": AffectState(**copy.deepcopy(agent["state"])), "traits": copy.deepcopy(agent["traits"])}

def _reproduce(final_agents, cfg, rng, next_generation, population_size):
    n_pairs = max(1, population_size // 2)
    parent_pairs = _pick_parents(final_agents, rng, n_pairs)
    children = []
    idx = 1
    for pa_dict, pb_dict in parent_pairs:
        pa = _agent_dict_to_parent(pa_dict)
        pb = _agent_dict_to_parent(pb_dict)
        for _ in range(2):
            genome = derive_child(pa, pb, rng, cfg.mutation_strength)
            children.append(Agent(agent_id=f"g{next_generation}_{idx}", lineage=f"{pa_dict['lineage']}__x__{pb_dict['lineage']}", state=genome.state, traits=genome.traits))
            idx += 1
    return children[:population_size]

def _run_population_simulation(cfg, society_cfg, population):
    agents = population
    society = SocietyField(**society_cfg.__dict__)
    for step in range(cfg.steps):
        active_states = [a.state for a in agents if not a.collapsed]
        if not active_states:
            break
        group_mean = mean_state(active_states)
        for agent in agents:
            if agent.collapsed:
                continue
            stimulus = agent.perceive_stimulus(random.Random(cfg.seed + step + len(agent.agent_id)), cfg.stimulus_strength)
            agent.update(step, stimulus, group_mean, random.Random(cfg.seed+step), cfg.drift_strength, cfg.interaction_strength,
                         cfg.energy_drain_rate, cfg.plasticity_cost_weight, cfg.recovery_rate,
                         cfg.recovery_coherence_threshold, cfg.recovery_arousal_ceiling,
                         cfg.plasticity_window, cfg.plasticity_floor, cfg.plasticity_ceiling)
            if cfg.run_with_society:
                society.apply(agent.state, active_states)
            metrics = agent.compute_metrics(cfg.collapse_window)
            agent.remember(step, metrics)
            if metrics["collapse_risk"] > cfg.high_instability_threshold or agent.state.stability < cfg.collapse_threshold:
                agent.collapsed = True
                agent.collapse_type = agent.classify_collapse(metrics)
            else:
                agent.survival_profile = agent._classify_survival()
    for a in agents:
        if not a.collapsed:
            a.finalize_profile()
    final_agents = [a.to_dict() for a in agents]
    living = [a for a in agents if not a.collapsed]
    profile_counts = {}
    collapse_counts = {}
    for a in final_agents:
        key = a.get("survival_profile") or "collapsed"
        profile_counts[key] = profile_counts.get(key, 0) + 1
        if a.get("collapse_type"):
            collapse_counts[a["collapse_type"]] = collapse_counts.get(a["collapse_type"], 0) + 1
    return {
        "living_agents": len(living),
        "collapsed_agents": len(agents) - len(living),
        "final_mean_stability": round(statistics.mean([a.state.stability for a in agents]), 4),
        "final_mean_energy": round(statistics.mean([a.energy for a in agents]), 4),
        "final_mean_coherence": round(statistics.mean([a.state.coherence for a in agents]), 4),
        "profile_counts": profile_counts,
        "collapse_counts": collapse_counts,
        "final_agents": final_agents,
    }

def run_generations(num_generations=12, population_size=6, children_per_pair=2, stimulus_strength=0.18, base_output_dir="outputs/generations"):
    cfg = SimulationConfig()
    society_cfg = SocietyConfig()
    cfg.stimulus_strength = stimulus_strength
    rng = random.Random(cfg.seed)
    os.makedirs(base_output_dir, exist_ok=True)
    population = _seed_population_from_pairs(cfg, rng, children_per_pair)
    history = []
    for gen in range(num_generations):
        summary = _run_population_simulation(cfg, society_cfg, population)
        final_agents = summary["final_agents"]
        history.append({
            "generation": gen,
            "stimulus_strength": stimulus_strength,
            "living_agents": summary["living_agents"],
            "collapsed_agents": summary["collapsed_agents"],
            "final_mean_stability": summary["final_mean_stability"],
            "final_mean_energy": summary["final_mean_energy"],
            "final_mean_coherence": summary["final_mean_coherence"],
            "profile_counts": summary["profile_counts"],
            "collapse_counts": summary["collapse_counts"],
        })
        if gen < num_generations - 1:
            population = _reproduce(final_agents, cfg, rng, gen+1, population_size)
    history_path = os.path.join(base_output_dir, "generation_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return {"history": history, "history_path": history_path}
