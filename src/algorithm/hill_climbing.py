import random
from typing import Optional
from core.registry import Registry
from core.schedule import Schedule
from core.objective import ScheduleObjective


class SteepestAscentHillClimbing:
    def __init__(self, registry: Registry, max_iterations: Optional[int] = None):
        self.registry = registry
        self.max_iterations = max_iterations
        self.objective = ScheduleObjective(registry)
    
    def generate_neighbors(self, schedule: Schedule) -> list:
        neighbors = []
        placed_meetings = [self.registry.meetings[mid] for mid in schedule.where_is.keys()]
        
        for meeting in placed_meetings:
            current_pos = schedule.get_position(meeting.meeting_id)
            if current_pos is None:
                continue
            
            curr_day, curr_hour, curr_room = current_pos
            legal_rooms = self.registry.legal_classrooms_by_meeting.get(meeting.meeting_id, [])
            
            # Use the schedule's available days and hours
            days = schedule.days
            hours = schedule.hours
            
            for day in days:
                # Find valid starting hours for this meeting duration
                for hour in hours:
                    # Check if meeting can fit starting from this hour
                    if hour + meeting.duration_hours > max(hours) + 1:
                        continue
                    
                    # Check if all required hours are available in the schedule
                    required_hours = list(range(hour, hour + meeting.duration_hours))
                    if not all(h in hours for h in required_hours):
                        continue
                    
                    for room in legal_rooms:
                        if (day, hour, room) == (curr_day, curr_hour, curr_room):
                            continue
                        
                        can_move = True
                        for h in required_hours:
                            if not schedule.is_empty(day, h, room):
                                can_move = False
                                break
                        
                        if can_move:
                            # Create new schedule with same dimensions as current
                            new_schedule = Schedule(days, hours, schedule.classroom_codes)
                            
                            for m in placed_meetings:
                                pos = schedule.get_position(m.meeting_id)
                                if pos and m.meeting_id != meeting.meeting_id:
                                    new_schedule.place(m.meeting_id, pos[0], pos[1], pos[2])
                            
                            new_schedule.place(meeting.meeting_id, day, hour, room)
                            neighbors.append(new_schedule)
        
        return neighbors
    
    def run(self) -> tuple[Schedule, float, list]:
        print("Generating initial solution...")
        current = Schedule.generate_random_schedule(self.registry)
        current_score = self.objective.evaluate(current)
        
        history = [current_score]
        iteration = 0
        
        print(f"Initial score: {current_score}")
        
        while self.max_iterations is None or iteration < self.max_iterations:
            iteration += 1
            
            neighbors = self.generate_neighbors(current)
            
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
