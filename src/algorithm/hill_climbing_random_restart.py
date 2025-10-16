import time
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
    
    def run(self) -> tuple[Schedule, Schedule, float, list, int, float, list]:
        start_time = time.time()
        global_best_schedule = None
        global_best_score = float('inf')
        global_history = []
        iterations_list = []
        
        initial_schedule = None
        
        for restart in range(self.max_restarts):
            current = Schedule.random_initial_assignment(self.registry)
            current_score = self.objective.evaluate(current)
            
            if restart == 0:
                initial_schedule = current
                global_history.append(current_score)
            
            iteration = 0
            
            while self.max_iterations_per_restart is None or iteration < self.max_iterations_per_restart:
                iteration += 1
                
                neighbors = generate_neighbors(current, self.registry)
                
                if not neighbors:
                    break
                
                best_neighbor = None
                best_score = current_score
                
                for neighbor in neighbors:
                    score = self.objective.evaluate(neighbor)
                    if score < best_score:
                        best_score = score
                        best_neighbor = neighbor
                
                if best_neighbor is None:
                    break
                
                current = best_neighbor
                current_score = best_score
                
                if restart == 0:
                    global_history.append(current_score)
                
                if current_score == 0:
                    break
            
            iterations_list.append(iteration)
            
            if current_score < global_best_score:
                global_best_score = current_score
                global_best_schedule = current
            
            if global_best_score == 0:
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        return initial_schedule, global_best_schedule, global_best_score, global_history, restart + 1, duration, iterations_list
