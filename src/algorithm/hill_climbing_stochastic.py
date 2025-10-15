import random
import copy
from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from .neighbors import generate_neighbors, generate_random_neighbor

class StochasticHillClimbing:
    def __init__(self, registry: Registry, max_iterations: Optional[int] = None):
        self.registry = registry
        self.max_iterations = max_iterations if max_iterations is not None else 1000
        self.objective = ScheduleObjective(registry)

    def run(self) -> tuple[Schedule, float, list]:
        current = Schedule.random_initial_assignment(self.registry)
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

            # Pilih satu neighbor secara acak
            next_schedule = random.choice(neighbors)
            next_score = self.objective.evaluate(next_schedule)

            # Hanya update jika neighbor lebih baik
            if next_score < current_score:
                current = next_schedule
                current_score = next_score

            history.append(current_score)

            if iteration % 10 == 0:
                print(f"Iteration {iteration}: score = {current_score}")

            if current_score == 0:
                print(f"Optimal solution found at iteration {iteration}")
                break

        print(f"Final score: {current_score}")
        return current, current_score, history

    # Tidak diperlukan random_func_choice karena neighbor dipilih acak di generate_random_neighbor
