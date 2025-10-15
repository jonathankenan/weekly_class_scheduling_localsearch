import random
from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from algorithm.neighbors import generate_neighbors


class SteepestAscentHillClimbing:
    def __init__(self, registry: Registry, max_iterations: Optional[int] = None):
        self.registry = registry
        self.max_iterations = max_iterations
        self.objective = ScheduleObjective(registry)
    
    def run(self) -> tuple[Schedule, float, list]:
        current = Schedule.generate_random_schedule(self.registry)
        current_score = self.objective.evaluate(current)
        
        history = [current_score]
        iteration = 0
        
        print(f"Initial score: {current_score}")
        
        while self.max_iterations is None or iteration < self.max_iterations:
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
                print(f"Local optimum reached at iteration {iteration}")
                break
            
            current = best_neighbor
            current_score = best_score
            history.append(current_score)
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: score = {current_score}")
            
            if current_score == 0:
                print(f"Optimal solution found at iteration {iteration}")
                break
        
        print(f"Final score: {current_score}")
        return current, current_score, history
