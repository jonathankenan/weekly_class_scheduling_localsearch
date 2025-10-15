import sys
from pathlib import Path
import matplotlib.pyplot as plt
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.registry import Registry
from core.objective import ScheduleObjective
from algorithm.stimulated_annealing import SimulatedAnnealing


def main():
    print("="*60)
    print("TEST - SIMULATED ANNEALING")
    print("="*60)
    
    file_path = "../data/input/challenging_test.json"
    print("\n1. Loading data...")
    
    reg = Registry()
    reg.load_from_json(file_path)
    
    print(f"   Courses: {len(reg.courses)}")
    print(f"   Classrooms: {len(reg.classrooms)}")
    print(f"   Students: {len(reg.students)}")
    print(f"   Meetings: {len(reg.meetings)}")
    
    print("\n2. Running Simulated Annealing...")
    print("   (Max iterations: 1000)")
    print("   (Initial temperature: 100.0)")
    print("   (Cooling rate: 0.99)")

    # Uji coba dengan random generator yang di-seed
    rng = random.Random(42)
    sa_seeded = SimulatedAnnealing(reg, max_iterations=1000, initial_temp=100.0, cooling_rate=0.99, random_func=rng.random)
    best_seeded, best_score_seeded, score_history_seeded, acceptance_prob_history_seeded, stuck_count_seeded = sa_seeded.run()
    print("\n[Seeded RNG] Final best:", best_score_seeded)
    print("[Seeded RNG] Stuck count:", stuck_count_seeded)

    # Uji coba default (tanpa seed)
    sa = SimulatedAnnealing(reg, max_iterations=1000, initial_temp=100.0, cooling_rate=0.99)
    best, best_score, score_history, acceptance_prob_history, stuck_count = sa.run()
    print("\n[Default RNG] Final best:", best_score)
    print("[Default RNG] Stuck count:", stuck_count)

    # Uji coba dengan random_func yang selalu mengembalikan 0.7
    sa_fixed = SimulatedAnnealing(reg, max_iterations=1000, initial_temp=100.0, cooling_rate=0.99, random_func=lambda: 0.7)
    best_fixed, best_score_fixed, score_history_fixed, acceptance_prob_history_fixed, stuck_count_fixed = sa_fixed.run()
    print("\n[Fixed random_func=0.7] Final best:", best_score_fixed)
    print("[Fixed random_func=0.7] Stuck count:", stuck_count_fixed)
    
    print("\n3. Optimization results:")
    print(f"   Initial conflicts: {score_history[0]}")
    print(f"   Final best: {best_score}")
    print(f"   Total iterations: {len(score_history)}")
    print(f"   Improvement: {score_history[0] - best_score}")
    print(f"   Stuck count: {stuck_count}")
    
    placed_meetings = len(list(best.iter_assignments()))
    print(f"\n4. Schedule verification:")
    print(f"   Scheduled meetings: {placed_meetings}/{len(reg.meetings)}")
    if placed_meetings == len(reg.meetings):
        print(f"   Status: All meetings scheduled")
    else:
        print(f"   Status: Some meetings not scheduled")
    
    print(f"\n5. Sample schedule (first 5 meetings):")
    for idx, (mid, day, hour, room) in enumerate(best.iter_assignments()):
        if idx >= 5:
            break
        meeting = reg.meetings[mid]
        print(f"   Meeting {mid} ({meeting.course_code}): {day} at {hour}:00 in room {room}")
    
    print("\n" + "="*60)
    if best_score == 0:
        print("SUCCESS: Optimal solution found (no conflicts)")
    else:
        print(f"Best solution found with {best_score} conflicts")
    print("="*60)
    
    print("\n6. Creating plots...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    ax1.plot(range(len(score_history)), score_history, 'r-', linewidth=2, label='Objective Function')
    ax1.set_xlabel('Iteration', fontsize=12)
    ax1.set_ylabel('Objective Function Value (Conflicts)', fontsize=12)
    ax1.set_title('Simulated Annealing - Objective Function Progress', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    ax1.annotate(f'Start: {score_history[0]} conflicts', 
                xy=(0, score_history[0]), 
                xytext=(10, 10), 
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax1.annotate(f'End: {score_history[-1]} conflicts', 
                xy=(len(score_history)-1, score_history[-1]), 
                xytext=(10, -30), 
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='lightcoral', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax2.plot(range(len(acceptance_prob_history)), acceptance_prob_history, 'b-', linewidth=1, alpha=0.7, label='e^(ΔE/T)')
    ax2.set_xlabel('Iteration', fontsize=12)
    ax2.set_ylabel('Acceptance Probability', fontsize=12)
    ax2.set_title('Simulated Annealing - Acceptance Probability (e^(ΔE/T))', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, 1.05)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    textstr = f'Stuck count: {stuck_count}\nFinal best: {best_score}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig('../data/output/simulated_annealing_plot.png', dpi=300, bbox_inches='tight')
    print("   Plot saved to: data/output/simulated_annealing_plot.png")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)


if __name__ == "__main__":
    main()
