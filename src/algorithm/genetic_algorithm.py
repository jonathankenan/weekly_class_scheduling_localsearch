from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective
from typing import Optional
import random


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
            schedule = Schedule.generate_random_schedule(self.registry)
            self.population.append(schedule)
        print("Successfully initialized population")
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
    def one_point_crossover(self, parent1: Schedule, parent2: Schedule):
        # 1) Group each parent's mid by it's course code
        # Expected output: a Dict
        meetings_by_course = {}
        for meeting_id in parent1.where_is.keys():
            meeting = self.registry.meetings[meeting_id]
            course_code = meeting.course_code
            if course_code not in meetings_by_course:
                meetings_by_course[course_code] = []
            meetings_by_course[course_code].append(meeting_id) 

        # 1.5) Sort the meetings by course_code
        sorted_courses = sorted(meetings_by_course.keys())

        if len(sorted_courses) <= 1:
            return parent1, parent2  # Not enough to crossover

        # 2) Select Crossover Point
        #  Select a random point (1, len(sorted_courses)-1)
        crossover_point = random.randint(1, len(meetings_by_course) - 1)

        # 3) Create 2 childs
        child1 = Schedule(
        days=parent1.days,
        hours=parent1.hours,  
        classroom_codes=parent1.classroom_codes
        )
        
        child2 = Schedule(
            days=parent2.days,
            hours=parent2.hours,
            classroom_codes=parent2.classroom_codes
        )

        # 4) Cross over on crossover point (determine lhs and rhs by randint(1,2))
        for i, course_code in enumerate(sorted_courses):
            meeting_ids = meetings_by_course[course_code]
            
            if i < crossover_point:
                for meeting_id in meeting_ids:
                    day1, hour1, classroom1 = parent1.where_is[meeting_id]
                    child1.place(meeting_id, day1, hour1, classroom1)

                    day2, hour2, classroom2 = parent2.where_is[meeting_id]
                    child2.place(meeting_id, day2, hour2, classroom2)
            else:
                for meeting_id in meeting_ids:
                    day2, hour2, classroom2 = parent2.where_is[meeting_id]
                    child1.place(meeting_id, day2, hour2, classroom2)

                    day1, hour1, classroom1 = parent1.where_is[meeting_id]
                    child2.place(meeting_id, day1, hour1, classroom1)

        # 5) Assert length
        assert len(child1.where_is) == len(parent1.where_is), "Child1 missing meetings"
        assert len(child2.where_is) == len(parent2.where_is), "Child2 missing meetings"

        return child1, child2

    def crossover_population(self):
        # 1) Create offspring list
        offspring = []

        # 2) Process parents
        for i in range(0, len(self.parents) - 1, 2):
            parent1 = self.parents[i]
            parent2 = self.parents[i+1] # Logic has to use probability distribution in range

            child1, child2 = self.one_point_crossover(parent1, parent2)
            offspring.extend([child1, child2])

        if len(self.parents) % 2 == 1:
            offspring.append(self.parents[-1])

        # Validate all offspring
        for idx, child in enumerate(offspring):
            try:
                self._validate_schedule_credits(child) 
            except ValueError as e:
                print(f"Offspring {idx} failed validation: {e}")
                raise

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
        
        print(f"Mutation: {mutation_count}/{len(offspring)} improved")
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
    # Step 6: Main GA Loop
    def run(self, mutation_rate: float = 0.1) -> Schedule:
        """
        Run the genetic algorithm main loop.
        
        Args:
            mutation_rate: Probability of mutation (default: 0.1)
        
        Returns:
            Best schedule found
        """
        print("=" * 70)
        print("GENETIC ALGORITHM - COURSE SCHEDULING")
        print("=" * 70)
        print(f"Population size: {self.population_size}")
        print(f"Max iterations: {self.max_iteration}")
        print(f"Mutation rate: {mutation_rate}")
        print()
        
        # Step 1: Initialize population
        self.init_population()
        
        # Get initial best
        best_ever_schedule, best_ever_fitness = self.get_best_schedule(self.population)
        print(f"Initial best fitness: {best_ever_fitness:.2f}")
        print()
        
        # Main evolution loop
        for generation in range(self.max_iteration):
            print(f"--- Generation {generation + 1}/{self.max_iteration} ---")
            
            # Step 2: Parent selection
            self.parents = self.tournament_selection()
            print(f"Selected {len(self.parents)} parents")
            
            # Step 3: Crossover
            offspring = self.crossover_population()
            print(f"Generated {len(offspring)} offspring")
            
            # Step 4: Mutation
            offspring = self.mutate_population(offspring, mutation_rate)
            
            # Step 5: Replace population with offspring
            self.population = offspring
            
            # Evaluate current generation
            current_best_schedule, current_best_fitness = self.get_best_schedule(self.population)
            
            # Track best ever found
            if current_best_fitness < best_ever_fitness:
                improvement = best_ever_fitness - current_best_fitness
                best_ever_fitness = current_best_fitness
                best_ever_schedule = current_best_schedule
                print(f"NEW BEST! Fitness: {best_ever_fitness:.2f} (improved by {improvement:.2f})")
            else:
                print(f"Current best: {current_best_fitness:.2f} | Best ever: {best_ever_fitness:.2f}")
            
            # Check stopping condition: optimal solution (0 conflicts)
            if best_ever_fitness == 0:
                print()
                print("=" * 70)
                print("OPTIMAL SOLUTION FOUND!")
                print("=" * 70)
                print(f"Generation: {generation + 1}")
                print(f"Final fitness: {best_ever_fitness:.2f} (0 conflicts)")
                return best_ever_schedule
            
            print()
        
        # Max iterations reached
        print("=" * 70)
        print("GENETIC ALGORITHM COMPLETE")
        print("=" * 70)
        print(f"Best fitness achieved: {best_ever_fitness:.2f}")
        print(f"Total generations: {self.max_iteration}")
        print(f"Final conflicts: {best_ever_fitness:.0f}")
        
        return best_ever_schedule