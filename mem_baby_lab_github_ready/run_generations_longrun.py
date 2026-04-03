from evolution import run_generations
import json

for stimulus in [0.19, 0.22, 0.23]:
    result = run_generations(num_generations=30, population_size=6, children_per_pair=2, stimulus_strength=stimulus, base_output_dir=f"outputs/longrun_{str(stimulus).replace('.', '_')}")
    print(json.dumps({
        "stimulus": stimulus,
        "history_path": result["history_path"],
        "final": result["history"][-1]
    }, ensure_ascii=False, indent=2))
