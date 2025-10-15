import sys
from pathlib import Path
import matplotlib.pyplot as plt
import random

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.registry import Registry
from algorithm.hill_climbing_stochastic import StochasticHillClimbing

def main():
    print("="*60)
    print("TEST - STOCHASTIC HILL CLIMBING")
    print("="*60)
    
    file_path = "../data/input/challenging_test.json"
    print("\n1. Loading data...")
    reg = Registry()
    reg.load_from_json(file_path)
    print(f"   Courses: {len(reg.courses)}")
    print(f"   Classrooms: {len(reg.classrooms)}")
    print(f"   Students: {len(reg.students)}")
    print(f"   Meetings: {len(reg.meetings)}")
    
    print("\n2. Running Stochastic Hill Climbing...")
    shc = StochasticHillClimbing(reg, max_iterations=1000)
    best, best_score, score_history = shc.run()
    print(f"\nFinal best: {best_score}")
    print(f"Total iterations: {len(score_history)}")
    print(f"Improvement: {score_history[0] - best_score}")
    
    print("\n3. Creating plot...")
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(score_history)), score_history, 'g-', linewidth=2, label='Objective Function')
    plt.xlabel('Iteration')
    plt.ylabel('Objective Function Value (Conflicts)')
    plt.title('Stochastic Hill Climbing - Objective Function Progress')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../data/output/stochastic_hill_climbing_plot.png', dpi=300, bbox_inches='tight')
    print("   Plot saved to: data/output/stochastic_hill_climbing_plot.png")
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()
