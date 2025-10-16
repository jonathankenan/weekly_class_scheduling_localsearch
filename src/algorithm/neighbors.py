import random
from core.registry import Registry
from core.schedule import Schedule


def generate_neighbors(schedule: Schedule, registry: Registry) -> list:
    neighbors = []
    placed_meetings = [registry.meetings[mid] for mid in schedule.where_is.keys()]
    
    for meeting in placed_meetings:
        current_pos = schedule.get_position(meeting.meeting_id)
        if current_pos is None:
            continue
        
        curr_day, curr_hour, curr_room = current_pos
        legal_rooms = registry.legal_classrooms_by_meeting.get(meeting.meeting_id, [])
        
        days = schedule.days
        hours = schedule.hours
        
        for day in days:
            for hour in hours:
                if hour + meeting.duration_hours > max(hours) + 1:
                    continue
                
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
                        new_schedule = Schedule(days, hours, schedule.classroom_codes)
                        
                        for m in placed_meetings:
                            pos = schedule.get_position(m.meeting_id)
                            if pos and m.meeting_id != meeting.meeting_id:
                                new_schedule.place(m.meeting_id, pos[0], pos[1], pos[2])
                        
                        new_schedule.place(meeting.meeting_id, day, hour, room)
                        neighbors.append(new_schedule)
    
    return neighbors

def generate_random_neighbor(schedule: Schedule, registry: Registry) -> Schedule:
    neighbors = generate_neighbors(schedule, registry)
    if not neighbors:
        return schedule
    return random.choice(neighbors)
