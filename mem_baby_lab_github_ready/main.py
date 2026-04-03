from config import SimulationConfig, SocietyConfig
from simulation import run_simulation

def main():
    sim_cfg = SimulationConfig()
    society_cfg = SocietyConfig()
    summary = run_simulation(sim_cfg, society_cfg)
    print("\n=== M.E.M. Baby Lab ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
