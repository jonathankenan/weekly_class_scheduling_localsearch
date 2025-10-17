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

    # Input JSON filename
    print("\nAvailable test files: small, medium, big, large_test")
    json_filename = input("Enter JSON filename (without .json extension, default: big): ").strip()
    if not json_filename:
        json_filename = "big"
    
    file_path = f"data/input/{json_filename}.json"
    print(f"\nLoading data from: {file_path}")

    try:
        reg = Registry()
        reg.load_from_json(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found!")
        return

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
    print("\n" + "-"*60)
    print("ALGORITHM PARAMETERS")
    print("-"*60)

    # Initialize algorithm with user-defined parameters
    objective = ScheduleObjective(reg)

    if choice == 1:  # Steepest Ascent
        max_iter = input("Max iterations (default: None): ").strip()
        max_iter = int(max_iter) if max_iter else None
        print(f"Running with max_iterations={max_iter}")
        hc = algorithm_class(reg, max_iterations=max_iter)
        
    elif choice == 2:  # Stochastic
        max_iter = input("Max iterations (default: None): ").strip()
        max_iter = int(max_iter) if max_iter else None
        print(f"Running with max_iterations={max_iter}")
        hc = algorithm_class(reg, max_iterations=max_iter)
        
    elif choice == 3:  # Simulated Annealing
        initial_temp = input("Initial temperature (default: 1000): ").strip()
        initial_temp = float(initial_temp) if initial_temp else 1000
        
        cooling_rate = input("Cooling rate (default: 0.95): ").strip()
        cooling_rate = float(cooling_rate) if cooling_rate else 0.95
        
        max_iter = input("Max iterations (default: None): ").strip()
        max_iter = int(max_iter) if max_iter else None

        random_func = input("Probability threshold value (default: None (Random)): ").strip()
        random_func = float(random_func) if random_func else None

        print(f"Running with initial_temp={initial_temp}, cooling_rate={cooling_rate}, max_iterations={max_iter}")
        hc = algorithm_class(reg, initial_temp=initial_temp, cooling_rate=cooling_rate, max_iterations=max_iter, random_func=random_func)
        
    elif choice == 4:  # Sideways
        max_consec = input("Max consecutive sideways moves (default: 5): ").strip()
        max_consec = int(max_consec) if max_consec else 5
        
        max_total = input("Max total sideways moves (default: 20): ").strip()
        max_total = int(max_total) if max_total else 20
        
        max_iter = input("Max iterations (default: None): ").strip()
        max_iter = int(max_iter) if max_iter else None
        
        print(f"Running with max_consecutive={max_consec}, max_total={max_total}, max_iterations={max_iter}")
        hc = algorithm_class(reg, max_consecutive_sideways=max_consec, max_total_sideways=max_total, max_iterations=max_iter)
        
    elif choice == 5:  # Random Restart
        max_restarts = input("Max restarts (default: 10): ").strip()
        max_restarts = int(max_restarts) if max_restarts else 10
        
        max_iter_per_restart = input("Max iterations per restart (default: None): ").strip()
        max_iter_per_restart = int(max_iter_per_restart) if max_iter_per_restart else None
        
        print(f"Running with max_restarts={max_restarts}, max_iterations_per_restart={max_iter_per_restart}")
        hc = algorithm_class(reg, max_restarts=max_restarts, max_iterations_per_restart=max_iter_per_restart)
        
    elif choice == 6:  # Genetic Algorithm
        pop_size = input("Population size (default: 50): ").strip()
        pop_size = int(pop_size) if pop_size else 50
        
        max_iter = input("Max generations (default: 100): ").strip()
        max_iter = int(max_iter) if max_iter else 100
        
        mut_rate = input("Mutation rate (default: 0.15): ").strip()
        mut_rate = float(mut_rate) if mut_rate else 0.15
        
        print(f"Running with population_size={pop_size}, max_generations={max_iter}, mutation_rate={mut_rate}")
        hc = algorithm_class(reg, population_size=pop_size, max_iteration=max_iter)



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
        initial_schedule, best_schedule, best_score, history, generations_run, duration = hc.run(mutation_rate=mut_rate)
        
        # Display initial state
        print("\nInitial Best Schedule:")
        initial_schedule.display(reg)
        plot_schedule_visualization(initial_schedule, f'{algorithm_name} - Initial Schedule', reg)
        
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

    plt.xlabel('Iteration' if choice != 6 else 'Generation', fontsize=12)
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
    elif choice == 6:  # Genetic Algorithm
        info_text += f'\nGenerations: {generations_run}\nPopulation: {pop_size}'

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
