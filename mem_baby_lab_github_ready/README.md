# M.E.M. Baby Lab

A small simulation lab for exploring agent development, stability, collapse, recovery, and multi-generation evolution.

## Included

- `main.py` — runs a single baseline simulation
- `run_generations.py` — runs a multi-generation evolution experiment
- `run_generations_threshold.py` — compares threshold behavior across stimulus levels
- `run_generations_longrun.py` — runs longer experiments at selected stimulus levels
- `outputs/` — example output files from a successful run

## Requirements

- Python 3.10+
- `matplotlib>=3.8`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

### Windows PowerShell

```powershell
py main.py
py run_generations.py
py run_generations_threshold.py
py run_generations_longrun.py
```

### macOS / Linux

```bash
python main.py
python run_generations.py
python run_generations_threshold.py
python run_generations_longrun.py
```

## Output

The project writes JSON outputs to the `outputs/` folder, including:

- `run_summary.json`
- `final_agents.json`
- `timeline.json`

Additional generation and threshold experiments create subfolders inside `outputs/`.

## Notes before publishing on GitHub

This version is runnable and complete enough to upload.
What it does **not** include yet:

- a license file
- automated tests
- screenshots or plots in the README
- a fuller research explanation of the model assumptions

It also originally contained `__pycache__` files in the zip. Those are not needed in GitHub, so they were removed in this cleaned version.
