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
    
    def run(self) -> tuple[Schedule, float, list, int]:
        current = Schedule.generate_random_schedule(self.registry)
        current_score = self.objective.evaluate(current)
        
        history = [current_score]
        iteration = 0
        consecutive_sideways = 0
        total_sideways = 0
        
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
                if score <= best_score:
                    best_score = score
                    best_neighbor = neighbor
            
            if best_neighbor is None:
                print(f"Local optimum reached at iteration {iteration}")
                break
            
            if best_score == current_score:
                consecutive_sideways += 1
                total_sideways += 1
                
                if consecutive_sideways >= self.max_consecutive_sideways:
                    print(f"Max consecutive sideways moves ({self.max_consecutive_sideways}) reached at iteration {iteration}")
                    break
                
                if total_sideways >= self.max_total_sideways:
                    print(f"Max total sideways moves ({self.max_total_sideways}) reached at iteration {iteration}")
                    break
            else:
                consecutive_sideways = 0
            
            current = best_neighbor
            current_score = best_score
            history.append(current_score)
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: score = {current_score}, sideways = {consecutive_sideways}")
            
            if current_score == 0:
                print(f"Optimal solution found at iteration {iteration}")
                break
        
        print(f"Final score: {current_score}")
        print(f"Total sideways moves: {total_sideways}")
        
        return current, current_score, history, total_sideways
