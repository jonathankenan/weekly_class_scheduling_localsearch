# Fitness Function: Use ObjFunc


# Step 1: Initialize Population
# init_population(total_population)

# Evaluate Population with ObjFunc

# Step 2: Choose Parents
# Strategy -> Choose the top 2 states based on the fitness function


# Step 3: Crossover (Recombination)
# Strategy -> Use one-point crossover. Explore other options
# One-point crossover func, split by sorted index (day + timeslots).
# crossover(total_iteration)

# Step 4: Mutation
# Change a random room in legal_classrooms_by_meeting
# Use a randomizer func to change which meetings get's moved to a different slot.

# Step 5: Evaluation
# Save the best 1-2 states.
# Use Evaluation func.

# Step 6: Replacement 

# Stop condition: max_generations/no significant improvement in fitness function/reached goal.