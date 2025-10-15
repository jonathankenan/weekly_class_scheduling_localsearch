from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from algorithm.neighbors import generate_neighbors


class RandomRestartHillClimbing:
    def __init__(self, registry: Registry, max_restarts: int, max_iterations_per_restart: Optional[int] = None):
        self.registry = registry
        self.max_restarts = max_restarts
        self.max_iterations_per_restart = max_iterations_per_restart
        self.objective = ScheduleObjective(registry)
    
    def run(self) -> tuple[Schedule, float, list, int]:
        global_best_schedule = None
        global_best_score = float('inf')
        global_history = []
        
        print(f"Starting Random Restart Hill Climbing with max {self.max_restarts} restarts")
        
        for restart in range(self.max_restarts):
            print(f"\nRestart {restart + 1}/{self.max_restarts} ---")
            
            current = Schedule.generate_random_schedule(self.registry)
            current_score = self.objective.evaluate(current)
            
            print(f"Initial score: {current_score}")
            
            if restart == 0:
                global_history.append(current_score)
            
            iteration = 0
            
            while self.max_iterations_per_restart is None or iteration < self.max_iterations_per_restart:
                iteration += 1
                
                neighbors = generate_neighbors(current, self.registry)
                
                if not neighbors:
                    print(f"No neighbors found at iteration {iteration}")
                    break
                
                best_neighbor = None
                best_score = current_score
                
                for neighbor in neighbors:
                    score = self.objective.evaluate(neighbor)
                    if score < best_score:
                        best_score = score
                        best_neighbor = neighbor
                
                if best_neighbor is None:
                    print(f"Local optimum reached at iteration {iteration} with score {current_score}")
                    break
                
                current = best_neighbor
                current_score = best_score
                
                if restart == 0:
                    global_history.append(current_score)
                
                if current_score == 0:
                    print(f"Optimal solution found at iteration {iteration}")
                    break
            
            print(f"Restart {restart + 1} final score: {current_score}")
            
            if current_score < global_best_score:
                global_best_score = current_score
                global_best_schedule = current
                print(f"New global best: {global_best_score}")
            
            if global_best_score == 0:
                print(f"\nOptimal solution found! Stopping early at restart {restart + 1}")
                break
        
        print(f"\nFinal global best score: {global_best_score}")
        print(f"Total restarts performed: {restart + 1}")
        
        return global_best_schedule, global_best_score, global_history, restart + 1
