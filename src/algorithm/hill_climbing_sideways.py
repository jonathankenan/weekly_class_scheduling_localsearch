import time
from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from algorithm.neighbors import generate_neighbors


class HillClimbingSidewaysMove:
    def __init__(self, registry: Registry, max_consecutive_sideways: int, max_total_sideways: int, max_iterations: Optional[int] = None):
        self.registry = registry
        self.max_consecutive_sideways = max_consecutive_sideways
        self.max_total_sideways = max_total_sideways
        self.max_iterations = max_iterations
        self.objective = ScheduleObjective(registry)
    
    def run(self) -> tuple[Schedule, Schedule, float, list, float, int]:
        start_time = time.time()
        initial_schedule = Schedule.random_initial_assignment(self.registry)
        current = initial_schedule
        current_score = self.objective.evaluate(current)
        
        history = [current_score]
        iteration = 0
        consecutive_sideways = 0
        total_sideways = 0
        
        while self.max_iterations is None or iteration < self.max_iterations:
            iteration += 1
            
            neighbors = generate_neighbors(current, self.registry)
            
            if not neighbors:
                break
            
            best_neighbor = None
            best_score = current_score
            
            for neighbor in neighbors:
                score = self.objective.evaluate(neighbor)
                if score <= best_score:
                    best_score = score
                    best_neighbor = neighbor
            
            if best_neighbor is None:
                break
            
            if best_score == current_score:
                consecutive_sideways += 1
                total_sideways += 1
                
                if consecutive_sideways >= self.max_consecutive_sideways:
                    break
                
                if total_sideways >= self.max_total_sideways:
                    break
            else:
                consecutive_sideways = 0
            
            current = best_neighbor
            current_score = best_score
            history.append(current_score)
            
            if current_score == 0:
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        return initial_schedule, current, current_score, history, duration, iteration
