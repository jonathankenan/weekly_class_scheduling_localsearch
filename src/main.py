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
from algorithm.genetic_algorithm import Genetic_Algorithm

def main():
    print("="*60)
    print("COURSE SCHEDULING OPTIMIZATION")
    print("="*60)

    # Load data from JSON
    file_path = "data/input/big.json"
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
        5: ("Random Restart Hill Climbing", RandomRestartHillClimbing),
        6: ("Genetic Algorithm", Genetic_Algorithm)
    }

    print("\nAvailable Algorithms:")
    for key, (name, _) in algorithms.items():
        print(f"{key}. {name}")

    while True:
        try:
            choice = int(input("\nSelect algorithm (1-6): "))
            if choice in algorithms:
                break
            else:
                print("Invalid choice. Please select 1-6.")
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
    elif choice == 6:  # Genetic Algorithm
        hc = algorithm_class(reg, population_size=50, max_iteration=100)

    # Generate initial random schedule (not needed for GA)
    if choice != 6:
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

    elif choice == 6:  # Genetic Algorithm
        initial_schedule, best_schedule, best_score, history, generations_run, duration = hc.run(mutation_rate=0.15)
        
        # Display initial state
        print("\nInitial Best Schedule:")
        initial_schedule.display(reg)
        plot_schedule_visualization(initial_schedule, f'{algorithm_name} - Initial Best', reg)
        
        # Display final state
        print("\nFinal Best Schedule:")
        best_schedule.display(reg)
        plot_schedule_visualization(best_schedule, f'{algorithm_name} - Final Best', reg)
        
        print(f"\nFinal Objective Value: {best_score}")
        print(f"\nGenerations Run: {generations_run}")
        print(f"\nSearch Duration: {duration:.4f} seconds")
        print(f"\nConvergence History: {history[:10]}...")  # Show first 10


    # Create plot
    print("\n" + "="*60)
    print("GENERATING PLOT")
    print("="*60)

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(history)), history, 'b-o', linewidth=2, markersize=4, label='Objective Function')

    plt.xlabel('Iteration' if choice != 6 else 'Generation', fontsize=12)
    plt.ylabel('Objective Function Value (Conflicts)', fontsize=12)
    plt.title(f'{algorithm_name} - Optimization Progress', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)

    # Add annotations
    plt.annotate(f'Start: {history[0]}', xy=(0, history[0]), xytext=(10, 10),
                textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    plt.annotate(f'End: {history[-1]}', xy=(len(history)-1, history[-1]), xytext=(10, -30),
                textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='lightblue', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # Add info box
    info_text = f'Final Score: {best_score}\nDuration: {duration:.4f}s'
    if choice == 5:  # Random Restart
        info_text += f'\nRestarts: {total_restarts}\nIterations/Restart: {iterations_list}'
    elif choice == 3:  # Simulated Annealing
        info_text += f'\nStuck: {stuck_count}'
    elif choice == 6:  # Genetic Algorithm
        info_text += f'\nGenerations: {generations_run}\nPopulation: 50'

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
                course_codes = set()
                for mid in schedule.occupancy[(day, hour)].values():
                    if mid is not None:
                        meeting = registry.get_meeting(mid)
                        course_codes.add(meeting.course_code)
                
                if course_codes:
                    codes_list = sorted(list(course_codes))
                    cell_content = "\n".join(codes_list)  # Multi-line for table
                else:
                    cell_content = "-"
            else:
                cell_content = "-"
            
            row_data.append(cell_content)
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
