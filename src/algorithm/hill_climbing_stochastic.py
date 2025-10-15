import random
import copy
import time
from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from .neighbors import generate_neighbors, generate_random_neighbor

class StochasticHillClimbing:
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

            # Pilih satu neighbor secara acak
            next_schedule = random.choice(neighbors)
            next_score = self.objective.evaluate(next_schedule)

            # Hanya update jika neighbor lebih baik
            if next_score < current_score:
                current = next_schedule
                current_score = next_score

            history.append(current_score)

            if current_score == 0:
                break

        end_time = time.time()
        duration = end_time - start_time
        return initial_schedule, current, current_score, history, duration, iteration
