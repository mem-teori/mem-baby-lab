from evolution import run_generations
import json

result = run_generations(num_generations=12, population_size=6, children_per_pair=2, stimulus_strength=0.18, base_output_dir="outputs/generations_run")
print(json.dumps({
    "history_path": result["history_path"],
    "final": result["history"][-1]
}, ensure_ascii=False, indent=2))
