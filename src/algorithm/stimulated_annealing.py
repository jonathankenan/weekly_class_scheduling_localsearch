import random
import math
import copy
from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from algorithm.neighbors import generate_random_neighbor


class SimulatedAnnealing:
	def __init__(self, registry: Registry, max_iterations: Optional[int] = None, initial_temp: float = 100.0, cooling_rate: float = 0.99, random_func: Optional[callable] = None):
		self.registry = registry
		self.max_iterations = max_iterations if max_iterations is not None else 1000
		self.initial_temp = initial_temp
		self.cooling_rate = cooling_rate
		self.objective = ScheduleObjective(registry)
		self.random_func = random_func if random_func is not None else random.random
	
	def run(self) -> tuple[Schedule, float, list, list, int]:
		current = Schedule.random_initial_assignment(self.registry)
		current_score = self.objective.evaluate(current)
		best = copy.deepcopy(current)
		best_score = current_score
		temp = self.initial_temp
		
		score_history = [current_score]
		acceptance_probability_history = []
		stuck_count = 0
		iterations_without_improvement = 0

		print(f"Initial score: {current_score}")

		for it in range(self.max_iterations):
			neighbor = generate_random_neighbor(current, self.registry)
			neighbor_score = self.objective.evaluate(neighbor)
			delta = neighbor_score - current_score
			
			if delta < 0:
				acceptance_prob = 1.0
			else:
				acceptance_prob = math.exp(-delta / (temp + 1e-8))
			
			acceptance_probability_history.append(acceptance_prob)

			if delta < 0 or self.random_func() < acceptance_prob:
				current = neighbor
				current_score = neighbor_score
				
				if current_score < best_score:
					best = copy.deepcopy(current)
					best_score = current_score
					iterations_without_improvement = 0
				else:
					iterations_without_improvement += 1
			else:
				iterations_without_improvement += 1
			
			score_history.append(current_score)
			
			if iterations_without_improvement >= 50:
				stuck_count += 1
				iterations_without_improvement = 0
			
			temp *= self.cooling_rate
			
			if it % 100 == 0:
				print(f"Iteration {it}: score = {current_score:.2f}, best = {best_score:.2f}, temp = {temp:.2f}, stuck = {stuck_count}")
			
			if best_score == 0:
				print(f"Optimal solution found at iteration {it}")
				break
		
		print(f"Final best score: {best_score}")
		print(f"Total stuck events: {stuck_count}")

		return best, best_score, score_history, acceptance_probability_history, stuck_count