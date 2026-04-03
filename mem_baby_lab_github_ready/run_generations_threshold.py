from evolution import run_generations
import json, os

stimuli = [0.19, 0.20, 0.21, 0.22, 0.23]
rows = []
for s in stimuli:
    result = run_generations(num_generations=12, population_size=6, children_per_pair=2, stimulus_strength=s, base_output_dir=f"outputs/threshold_{str(s).replace('.', '_')}")
    final = result["history"][-1]
    rows.append({
        "stimulus": s,
        "living": final["living_agents"],
        "stability": final["final_mean_stability"],
        "energy": final["final_mean_energy"],
        "profiles": final["profile_counts"],
        "collapse": final["collapse_counts"],
    })
out = "outputs/threshold_summary.json"
os.makedirs("outputs", exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print(json.dumps(rows, ensure_ascii=False, indent=2))
