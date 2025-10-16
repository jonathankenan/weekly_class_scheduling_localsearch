from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from typing import Optional
from typing import Tuple, List, Optional
import random
import time


class Genetic_Algorithm:
    def __init__(self, registry: Registry, population_size: int, max_iteration: int):
        self.registry = registry
        self.population_size = population_size
        self.max_iteration = max_iteration
        self.population = []
        self.parents = []
        self.objective = ScheduleObjective(self.registry)

# Step 1: Initialize Population
    def init_population(self):
        """
        Generate initial population of total = population_size random schedules
        """
        self.population = [] # Reset population
        for i in range (self.population_size):
            schedule = Schedule.random_initial_assignment(self.registry)
            self.population.append(schedule)
        # print("Successfully initialized population")
        schedule.display(self.registry)
        return self.population

# Step 2: Choose Parents
# Strategy -> use probability function. Evaluate each individual with the fitness function/ObjFunc
# Choose a total of [total_population] parents.

    def tournament_selection(self, tournament_size: Optional[int] = None):
        # Determine tournament size
        if not (tournament_size):
            if self.population_size < 5:
                tournament_size = 1
            elif self.population_size < 10:
                tournament_size = 2
            elif self.population_size < 20:
                tournament_size = 3
            else:
                tournament_size = 5
        
        population_scored = {}
        for schedule in self.population:
            score = self.objective.evaluate(schedule)
            population_scored[schedule] = score # Map candidates with score

        parents = []
        # Select [num of parents] population
        for i in range(self.population_size):
            candidates = random.sample(self.population, tournament_size)
            
            best_candidate = None
            best_score = float('inf')

            for candidate in candidates:
                score = population_scored[candidate]
                if score < best_score:
                    best_candidate = candidate
                    best_score = score
            
            parents.append(best_candidate)

        # Clear old parents
        self.parents = parents

        return self.parents

# Step 3: Crossover (Recombination)
# Strategy -> Use one-point crossover. Explore other options
# One-point crossover func, split by sorted index (day + timeslots).
# crossover(total_iteration)
    # In algorithm/genetic_algorithm.py

    def _find_and_place(self, schedule: Schedule, meeting_id: int, preferred_room: str) -> bool:
        """Helper to find any free spot for a meeting and place it."""
        legal_rooms = self.registry.legal_classrooms_by_meeting.get(meeting_id, [preferred_room])
        if not legal_rooms:
            return False
            
        random.shuffle(schedule.days)
        random.shuffle(schedule.hours)
        random.shuffle(legal_rooms)

        for day in schedule.days:
            for hour in schedule.hours:
                for room in legal_rooms:
                    if schedule.is_empty(day, hour, room):
                        schedule.place(meeting_id, day, hour, room)
                        return True
        return False # No free spot found

    def one_point_crossover(self, parent1: Schedule, parent2: Schedule):
        # 1) Collect ALL meeting IDs from both parents
        all_meeting_ids = set(parent1.where_is.keys()) | set(parent2.where_is.keys())
        
        # Group by course code
        meetings_by_course = {}
        for meeting_id in all_meeting_ids:
            meeting = self.registry.meetings[meeting_id]
            course_code = meeting.course_code
            if course_code not in meetings_by_course:
                meetings_by_course[course_code] = []
            meetings_by_course[course_code].append(meeting_id)

        # 2) Sort courses for a consistent crossover point
        sorted_courses = sorted(meetings_by_course.keys())

        if len(sorted_courses) <= 1:
            import copy
            return copy.deepcopy(parent1), copy.deepcopy(parent2)

        # 3) Select crossover point
        crossover_point = random.randint(1, len(sorted_courses) - 1)

        # 4) Create children as deep copies of parents
        import copy
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        # 5) Crossover by swapping courses after the crossover point
        for i, course_code in enumerate(sorted_courses):
            if i >= crossover_point:
                meeting_ids_to_swap = meetings_by_course[course_code]
                
                # Step A: Clear all meetings for this course from both children
                # This creates a clean slate to prevent duplicates or lost meetings.
                for mid in meeting_ids_to_swap:
                    pos1 = child1.get_position(mid)
                    if pos1:
                        child1.remove(*pos1)
                    pos2 = child2.get_position(mid)
                    if pos2:
                        child2.remove(*pos2)

                # Step B: Re-populate from the opposite parent's genes
                for mid in meeting_ids_to_swap:
                    # Give child1 the genes from parent2
                    p2_pos = parent2.get_position(mid)
                    if p2_pos:
                        # Try to place at the exact same position
                        was_placed = child1.place(mid, *p2_pos)
                        if not was_placed:
                            # If that spot is taken, find any other free spot
                            self._find_and_place(child1, mid, p2_pos[2])

                    # Give child2 the genes from parent1
                    p1_pos = parent1.get_position(mid)
                    if p1_pos:
                        # Try to place at the exact same position
                        was_placed = child2.place(mid, *p1_pos)
                        if not was_placed:
                            # If that spot is taken, find any other free spot
                            self._find_and_place(child2, mid, p1_pos[2])
                            
        return child1, child2
    
    def crossover_population(self):
        offspring = []

        for i in range(0, len(self.parents) - 1, 2):
            parent1 = self.parents[i]
            parent2 = self.parents[i+1]

            child1, child2 = self.one_point_crossover(parent1, parent2)
            
            # Validate 
            try:
                self._validate_schedule_credits(child1)
                self._validate_schedule_credits(child2)
                offspring.extend([child1, child2])
            except ValueError as e:
                print(f"Unexpected validation failure: {e}")
                # Fallback to parents
                import copy
                offspring.extend([copy.deepcopy(parent1), copy.deepcopy(parent2)])

        if len(self.parents) % 2 == 1:
            import copy
            offspring.append(copy.deepcopy(self.parents[-1]))

        # print(f"Generated {len(offspring)} offspring")
        return offspring

    def _validate_schedule_credits(self, schedule: Schedule):
        meetings_per_course = {} 
        for meeting_id in schedule.where_is.keys():
            meeting = self.registry.meetings[meeting_id]
            course_code = meeting.course_code
            meetings_per_course[course_code] = meetings_per_course.get(course_code, 0) + 1
        
        # Check against expected credits
        for course_code, count in meetings_per_course.items():
            expected_credits = self.registry.courses[course_code].credits
            if count != expected_credits:
                print(f"Schedule: Course {course_code} has {count} meetings, expected {expected_credits}")
                raise ValueError(f"Credit validation failed for {course_code}")
    
# Step 4: Mutation
# Change a random room in legal_classrooms_by_meeting
# Use a randomizer func to change which meetings get's moved to a different slot.
    def mutate_schedule(self, schedule: Schedule, mutation_rate: float = 0.1):
        # 1) Decide mutation action randomly
        mutation_type = random.choice(['swap', 'move', 'time_shift'])

        if random.random() > mutation_rate:
            return schedule  # No mutation
    
        if mutation_type == 'swap':
            # Swap two random meetings
            meeting_ids = list(schedule.where_is.keys())
            if len(meeting_ids) >= 2:
                mid1, mid2 = random.sample(meeting_ids, 2)
                pos1 = schedule.get_position(mid1)
                pos2 = schedule.get_position(mid2)
                
                if pos1 and pos2:
                    schedule.swap(pos1, pos2)
    
        elif mutation_type == 'move':
        # Move one meeting to a free position
            meeting_ids = list(schedule.where_is.keys())
            if meeting_ids:
                mid = random.choice(meeting_ids)
                old_pos = schedule.get_position(mid)
                
                # Get legal classrooms for this meeting
                meeting = self.registry.meetings[mid]
                legal_rooms = self.registry.legal_classrooms_by_meeting.get(mid, [])
                
                if legal_rooms and old_pos:
                    # Try random new position
                    new_day = random.choice(schedule.days)
                    new_hour = random.choice(schedule.hours)
                    new_room = random.choice(legal_rooms)
                    new_pos = (new_day, new_hour, new_room)
                    
                    # Only move if new position is free
                    if schedule.is_empty(new_day, new_hour, new_room):
                        schedule.move(old_pos, new_pos)

        elif mutation_type == 'time_shift':
        # Shift one meeting to adjacent time slot
            meeting_ids = list(schedule.where_is.keys())
            if meeting_ids:
                mid = random.choice(meeting_ids)
                old_pos = schedule.get_position(mid)
                
                if old_pos:
                    day, hour, room = old_pos
                    # Try shift +1 or -1 hour
                    new_hour = hour + random.choice([-1, 1])
                    if new_hour in schedule.hours:
                        new_pos = (day, new_hour, room)
                        if schedule.is_empty(day, new_hour, room):
                            schedule.move(old_pos, new_pos)
        return schedule

    def mutate_population(self, offspring: list[Schedule], mutation_rate: float = 0.1):
        mutated = []
        mutation_count = 0
        
        for schedule in offspring:
            original_fitness = self.objective.evaluate(schedule)
            mutated_schedule = self.mutate_schedule(schedule, mutation_rate)
            new_fitness = self.objective.evaluate(mutated_schedule)
            
            # Accept mutation if it improves or with small probability if worse
            if new_fitness <= original_fitness or random.random() < 0.1:
                mutated.append(mutated_schedule)
                if new_fitness < original_fitness:
                    mutation_count += 1
            else:
                mutated.append(schedule)  # Keep original
        
        # print(f"Mutation: {mutation_count}/{len(offspring)} improved")
        return mutated


    # Step 5: Evaluation
    def get_best_schedule(self, population: list[Schedule]) -> tuple[Schedule, float]:
        best_schedule = None
        best_fitness = float('inf')
        
        for schedule in population:
            fitness = self.objective.evaluate(schedule)
            if fitness < best_fitness:
                best_fitness = fitness
                best_schedule = schedule
        
        return best_schedule, best_fitness

# Main loop.
# Use Evaluation func. If already reached optimum global or max_iteration = stop

# Stop condition: max_generations/no significant improvement in fitness function/reached goal.

# Step 6: Main GA Loop
    def run(self, mutation_rate: float = 0.1) -> Tuple[Optional[Schedule], Optional[Schedule], float, List[float], int, float]:
        """
        Executes the genetic algorithm and returns detailed diagnostics.

        Args:
            mutation_rate: The probability of a mutation for each schedule.

        Returns:
            A tuple containing:
            - initial_best_schedule: The best schedule from the first generation.
            - global_best_schedule: The best schedule found across all generations.
            - global_best_score: The fitness score of the best schedule.
            - score_history: A list of the best score at each generation.
            - generations_run: The total number of generations executed.
            - duration: The total execution time in seconds.
        """
        start_time = time.time()

        # Step 1: Initialize Population
        self.init_population()
        if not self.population:
            return None, None, float('inf'), [], 0, time.time() - start_time
            
        initial_best_schedule, initial_best_fitness = self.get_best_schedule(self.population)
        
        best_ever_schedule = initial_best_schedule
        best_ever_fitness = initial_best_fitness
        score_history = [initial_best_fitness]
        generations_run = 0

        # Step 2: Main Evolution Loop
        for generation in range(self.max_iteration):
            generations_run += 1
            
            self.parents = self.tournament_selection()
            offspring = self.crossover_population()
            offspring = self.mutate_population(offspring, mutation_rate)
            self.population = offspring
            
            current_best_schedule, current_best_fitness = self.get_best_schedule(self.population)
            
            if current_best_fitness < best_ever_fitness:
                best_ever_fitness = current_best_fitness
                best_ever_schedule = current_best_schedule
            
            score_history.append(best_ever_fitness)
            
            if best_ever_fitness == 0:
                break
        
        # Step 3: Finalize and Return Results
        end_time = time.time()
        duration = end_time - start_time
        
        return (
            initial_best_schedule, 
            best_ever_schedule, 
            best_ever_fitness, 
            score_history, 
            generations_run, 
            duration
        )