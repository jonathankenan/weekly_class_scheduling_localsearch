import random
import time
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
    
    def run(self) -> tuple[Schedule, Schedule, float, list, float, int]:
        start_time = time.time()
        initial_schedule = Schedule.random_initial_assignment(self.registry)
        current = initial_schedule
        current_score = self.objective.evaluate(current)

        history = [current_score]
        iteration = 0

        while self.max_iterations is None or iteration < self.max_iterations:
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
            history.append(current_score)

            if current_score == 0:
                break

        end_time = time.time()
        duration = end_time - start_time
        return initial_schedule, current, current_score, history, duration, iteration
