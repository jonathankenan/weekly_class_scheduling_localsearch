import sys
import matplotlib.pyplot as plt
import numpy as np
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from core.models import DAY
from algorithm.hill_climbing_steepest_ascent import SteepestAscentHillClimbing
from algorithm.hill_climbing_stochastic import StochasticHillClimbing
from algorithm.stimulated_annealing import SimulatedAnnealing
from algorithm.hill_climbing_sideways import HillClimbingSidewaysMove
from algorithm.hill_climbing_random_restart import RandomRestartHillClimbing

def main():
    print("="*60)
    print("COURSE SCHEDULING OPTIMIZATION USING HILL CLIMBING ALGORITHMS")
    print("="*60)

    # Load data from JSON
    file_path = "data/input/large_test.json"
    print(f"\nLoading data from: {file_path}")

    reg = Registry()
    reg.load_from_json(file_path)

    print(f"Courses: {len(reg.courses)}")
    print(f"Classrooms: {len(reg.classrooms)}")
    print(f"Students: {len(reg.students)}")
    print(f"Meetings: {len(reg.meetings)}")

    # Algorithm selection menu
    algorithms = {
        1: ("Hill Climbing Steepest Ascent", SteepestAscentHillClimbing),
        2: ("Hill Climbing Stochastic", StochasticHillClimbing),
        3: ("Simulated Annealing", SimulatedAnnealing),
        4: ("Hill Climbing with Sideways Move", HillClimbingSidewaysMove),
        5: ("Random Restart Hill Climbing", RandomRestartHillClimbing)
    }

    print("\nAvailable Algorithms:")
    for key, (name, _) in algorithms.items():
        print(f"{key}. {name}")

    while True:
        try:
            choice = int(input("\nSelect algorithm (1-5): "))
            if choice in algorithms:
                break
            else:
                print("Invalid choice. Please select 1-5.")
        except ValueError:
            print("Please enter a number.")

    algorithm_name, algorithm_class = algorithms[choice]
    print(f"\nSelected: {algorithm_name}")

    # Initialize algorithm with default parameters
    objective = ScheduleObjective(reg)

    if choice == 1:  # Steepest Ascent
        hc = algorithm_class(reg, max_iterations=1000)
    elif choice == 2:  # Stochastic
        hc = algorithm_class(reg, max_iterations=1000)
    elif choice == 3:  # Simulated Annealing
        hc = algorithm_class(reg, initial_temp=1000, cooling_rate=0.95, max_iterations=1000)
    elif choice == 4:  # Sideways
        hc = algorithm_class(reg, max_consecutive_sideways=5, max_total_sideways=20, max_iterations=1000)
    elif choice == 5:  # Random Restart
        hc = algorithm_class(reg, max_restarts=10, max_iterations_per_restart=100)

    # Generate initial random schedule
    initial_schedule = Schedule.generate_random_schedule(reg)
    initial_score = objective.evaluate(initial_schedule)

    # Run the algorithm
    print("\n" + "="*60)
    print(f"RUNNING {algorithm_name.upper()}")
    print("="*60)

    if choice in [1, 2]:  # Steepest Ascent, Stochastic
        initial_schedule, best_schedule, best_score, history, duration, total_iterations = hc.run()
        
        # Display initial state
        print("\nInitial Schedule Table:")
        initial_schedule.print_schedule_table(reg)
        plot_schedule_visualization(initial_schedule, f'{algorithm_name} - Initial Schedule', reg)
        
        # Display final state
        print("\nFinal Schedule Table:")
        best_schedule.print_schedule_table(reg)
        plot_schedule_visualization(best_schedule, f'{algorithm_name} - Final Schedule', reg)
        print(f"\nFinal Objective Value: {best_score}")
        print(f"\nPlot Score: {history}")
        print(f"\nSearch Duration: {duration:.4f} seconds")
        print(f"\nTotal Iterations: {total_iterations}")

    elif choice == 3:  # Simulated Annealing
        initial_schedule, best_schedule, best_score, history, acceptance_history, stuck_count, duration = hc.run()
        
        # Display initial state
        print("\nInitial Schedule Table:")
        initial_schedule.print_schedule_table(reg)
        plot_schedule_visualization(initial_schedule, f'{algorithm_name} - Initial Schedule', reg)
        
        # Display final state
        print("\nFinal Schedule Table:")
        best_schedule.print_schedule_table(reg)
        plot_schedule_visualization(best_schedule, f'{algorithm_name} - Final Schedule', reg)
        print(f"\nFinal Objective Value: {best_score}")
        print(f"\nPlot Score: {history}")
        print(f"\nPlot Acceptance: {acceptance_history}")
        print(f"\nSearch Duration: {duration:.4f} seconds")
        print(f"Stuck Frequency: {stuck_count}")

    elif choice == 4:  # Sideways
        initial_schedule, best_schedule, best_score, history, duration, total_iterations = hc.run()
        
        # Display initial state
        print("\nInitial Schedule Table:")
        initial_schedule.print_schedule_table(reg)
        plot_schedule_visualization(initial_schedule, f'{algorithm_name} - Initial Schedule', reg)
        
        # Display final state
        print("\nFinal Schedule Table:")
        best_schedule.print_schedule_table(reg)
        plot_schedule_visualization(best_schedule, f'{algorithm_name} - Final Schedule', reg)
        print(f"\nFinal Objective Value: {best_score}")
        print(f"\nPlot Score: {history}")
        print(f"\nSearch Duration: {duration:.4f} seconds")
        print(f"\nTotal Iterations: {total_iterations}")

    elif choice == 5:  # Random Restart
        initial_schedule, best_schedule, best_score, history, total_restarts, duration, iterations_list = hc.run()
        
        # Display initial state
        print("\nInitial Schedule Table:")
        initial_schedule.print_schedule_table(reg)
        plot_schedule_visualization(initial_schedule, f'{algorithm_name} - Initial Schedule', reg)
        
        # Display final state
        print("\nFinal Schedule Table:")
        best_schedule.print_schedule_table(reg)
        plot_schedule_visualization(best_schedule, f'{algorithm_name} - Final Schedule', reg)
        print(f"\nFinal Objective Value: {best_score}")
        print(f"\nPlot Score: {history}")
        print(f"\nSearch Duration: {duration:.4f} seconds")
        print(f"\nTotal Restarts: {total_restarts}")
        print(f"\nIterations per Restart: {iterations_list}")


    # Create plot
    print("\n" + "="*60)
    print("GENERATING PLOT")
    print("="*60)

    # Handle history for Random Restart (list of lists)
    plt.figure(figsize=(10, 6))
    if choice == 5 and isinstance(history, list) and history:
        # Plot each restart as a separate line
        for i, hist in enumerate(history):
            if hist:  # Ensure hist is not empty
                plt.plot(range(len(hist)), hist, 'o-', linewidth=2, markersize=4, label=f'Restart {i+1}')
    else:
        plot_history = history
        plt.plot(range(len(plot_history)), plot_history, 'b-o', linewidth=2, markersize=4, label='Objective Function')

    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Objective Function Value (Conflicts)', fontsize=12)
    plt.title(f'{algorithm_name} - Optimization Progress', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)

    # Add annotations (simplified for multiple lines)
    if choice == 5 and isinstance(history, list) and history:
        # Annotate start and end for each restart
        for i, hist in enumerate(history):
            if hist:
                plt.annotate(f'Start R{i+1}: {hist[0]}', xy=(0, hist[0]), xytext=(10 + i*50, 10 + i*10),
                            textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
                plt.annotate(f'End R{i+1}: {hist[-1]}', xy=(len(hist)-1, hist[-1]), xytext=(10 + i*50, -30 - i*10),
                            textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='lightblue', alpha=0.7),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    else:
        if plot_history:
            plt.annotate(f'Start: {plot_history[0]}', xy=(0, plot_history[0]), xytext=(10, 10),
                        textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            plt.annotate(f'End: {plot_history[-1]}', xy=(len(plot_history)-1, plot_history[-1]), xytext=(10, -30),
                        textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='lightblue', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # Add info box
    info_text = f'Final Score: {best_score}\nDuration: {duration:.4f}s'
    if choice == 5:  # Random Restart
        info_text += f'\nRestarts: {total_restarts}\nIterations/Restart: {iterations_list}'
    elif choice == 3:  # Simulated Annealing
        info_text += f'\nStuck: {stuck_count}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.05, 0.95, info_text, transform=plt.gca().transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    plot_path = f'data/output/{algorithm_name.lower().replace(" ", "_")}_plot.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {plot_path}")

    # Additional plot for Simulated Annealing
    if choice == 3:
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(acceptance_history)), acceptance_history, 'r-o', linewidth=2, markersize=4, label='Acceptance Probability')

        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Acceptance Probability', fontsize=12)
        plt.title(f'{algorithm_name} - Acceptance Probability Progress', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)

        plt.tight_layout()
        acceptance_plot_path = f'data/output/{algorithm_name.lower().replace(" ", "_")}_acceptance_plot.png'
        plt.savefig(acceptance_plot_path, dpi=300, bbox_inches='tight')
        print(f"Acceptance plot saved to: {acceptance_plot_path}")

    print("\n" + "="*60)
    print("OPTIMIZATION COMPLETED")
    print("="*60)

def plot_schedule_visualization(schedule, title, registry, save_path=None):
    """
    Create a matplotlib table visualization showing course codes per time slot.
    """
    days = list(DAY)
    day_labels = [d.name for d in days]
    hours = list(range(7, 18))
    
    # Prepare data for table
    data = []
    row_labels = [f"{h}:00" for h in hours]
    
    for hour in hours:
        row_data = []
        for day in days:
            if (day, hour) in schedule.occupancy:
                room_contents = []
                for room in schedule.classroom_codes:
                    mid = schedule.occupancy[(day, hour)].get(room)
                    if mid is not None:
                        course_code = registry.get_meeting(mid).course_code
                        room_contents.append(f"{room}:{course_code}")
                if room_contents:
                    slot_content = "\n".join(room_contents)  # Multi-line for table
                else:
                    slot_content = "-"
            else:
                slot_content = "-"
            
            row_data.append(slot_content)
        data.append(row_data)
    
    # Create figure and table
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    table = ax.table(cellText=data, 
                    rowLabels=row_labels, 
                    colLabels=day_labels, 
                    cellLoc='center', 
                    loc='center',
                    colWidths=[0.15] * len(day_labels))
    
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1.5, 2.0)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Schedule visualization saved to: {save_path}")
    
    plt.show()


if __name__ == "__main__":
    main()
