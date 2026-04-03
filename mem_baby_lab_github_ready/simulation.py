from __future__ import annotations
import os, json, random, statistics
from config import SimulationConfig, SocietyConfig
from profiles import PARENT_PAIRS
from inheritance import derive_child
from agent import Agent
from affect_space import mean_state
from society import SocietyField

def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def build_agents(cfg, rng):
    agents = []
    for lineage, pair in PARENT_PAIRS.items():
        genome = derive_child(pair["parent_a"], pair["parent_b"], rng, cfg.mutation_strength)
        agents.append(Agent(agent_id=f"{lineage}_child", lineage=lineage, state=genome.state, traits=genome.traits))
    return agents

def run_simulation(cfg: SimulationConfig, society_cfg: SocietyConfig) -> dict:
    rng = random.Random(cfg.seed)
    agents = build_agents(cfg, rng)
    society = SocietyField(**society_cfg.__dict__)
    ensure_output_dir(cfg.output_dir)
    timeline = []
    for step in range(cfg.steps):
        active_states = [a.state for a in agents if not a.collapsed]
        if not active_states:
            break
        group_mean = mean_state(active_states)
        step_row = {"step": step, "agents": []}
        for agent in agents:
            if agent.collapsed:
                step_row["agents"].append({"agent_id": agent.agent_id, "collapsed": True})
                continue
            stimulus = agent.perceive_stimulus(rng, cfg.stimulus_strength)
            agent.update(step, stimulus, group_mean, rng, cfg.drift_strength, cfg.interaction_strength,
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
            step_row["agents"].append({
                "agent_id": agent.agent_id,
                "lineage": agent.lineage,
                "collapsed": agent.collapsed,
                "collapse_type": agent.collapse_type,
                "survival_profile": agent.survival_profile,
                "state": agent.state.as_dict(),
                "metrics": metrics,
            })
        timeline.append(step_row)
    for a in agents:
        if not a.collapsed:
            a.finalize_profile()
    final_agents = [a.to_dict() for a in agents]
    living = [a for a in agents if not a.collapsed]
    summary = {
        "total_agents": len(agents),
        "living_agents": len(living),
        "collapsed_agents": len(agents) - len(living),
        "final_mean_stability": round(statistics.mean([a.state.stability for a in agents]), 4),
        "final_mean_coherence": round(statistics.mean([a.state.coherence for a in agents]), 4),
        "final_mean_valence": round(statistics.mean([a.state.valence for a in agents]), 4),
        "final_mean_energy": round(statistics.mean([a.energy for a in agents]), 4),
        "survivors": [a.agent_id for a in living],
        "survival_profiles": {a.lineage: a.survival_profile for a in agents},
        "collapse_types": {a.lineage: a.collapse_type for a in agents if a.collapse_type},
    }
    with open(os.path.join(cfg.output_dir, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    with open(os.path.join(cfg.output_dir, "final_agents.json"), "w", encoding="utf-8") as f:
        json.dump(final_agents, f, ensure_ascii=False, indent=2)
    with open(os.path.join(cfg.output_dir, "run_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary
