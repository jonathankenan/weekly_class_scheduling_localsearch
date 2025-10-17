from __future__ import annotations
from typing import Dict, Optional, Tuple, List, TYPE_CHECKING
from core.models import DAY
import random

if TYPE_CHECKING:
    from core.registry import Registry

class Schedule:
    """
    Mutable state for weekly scheduling.
    Stores where each meeting_id is placed: (day, hour, classroom).
    Manages the complete schedule grid with efficient lookup and modification operations.
    """

    def __init__(self, days: List[DAY], hours: List[int], classroom_codes: List[str]):
        """
        Initialize empty schedule with given days, hours, and classrooms.
        
        Args:
            days: List of DAY enum values for scheduling
            hours: List of hour integers for time slots
            classroom_codes: List of classroom identifier strings
        """
        if not days or not hours or not classroom_codes:
            raise ValueError("days, hours, and classroom_codes must be non-empty")

        # Store schedule dimensions
        self.days: List[str] = list(days)
        self.hours: List[int] = list(hours)
        self.classroom_codes: List[str] = list(classroom_codes)

        # Fast membership checks using sets
        self._day_set = set(self.days)
        self._hour_set = set(self.hours)
        self._room_set = set(self.classroom_codes)

        # Main occupancy grid: (day, hour) -> {classroom: meeting_id or None}
        self.occupancy: Dict[Tuple[DAY, int], Dict[str, Optional[int]]] = {}
        for d in self.days:
            for h in self.hours:
                self.occupancy[(d, h)] = {room: None for room in self.classroom_codes}

        # Reverse index for fast meeting lookup: meeting_id -> (day, hour, classroom)
        self.where_is: Dict[int, Tuple[str, int, str]] = {}

    # ---------- Internal Helper Methods ----------
    def _check_pos(self, day: DAY, hour: int, classroom: str) -> None:
        """
        Validate that the given position exists in the schedule.
        
        Args:
            day: DAY enum value
            hour: Hour integer
            classroom: Classroom code string
            
        Raises:
            TypeError: If day is not a DAY enum
            ValueError: If hour or classroom is not in the schedule
        """
        if not isinstance(day, DAY):
            raise TypeError(f"day must be a DAY enum, got {day}")
        if hour not in self._hour_set:
            raise ValueError(f"Unknown hour: {hour}")
        if classroom not in self._room_set:
            raise ValueError(f"Unknown classroom: {classroom}")

    # ---------- Query Methods ----------
    def is_empty(self, day: str, hour: int, classroom: str) -> bool:
        """
        Check if a specific position in the schedule is empty.
        
        Args:
            day: Day string
            hour: Hour integer
            classroom: Classroom code string
            
        Returns:
            True if position is empty, False if occupied
        """
        self._check_pos(day, hour, classroom)
        return self.occupancy[(day, hour)][classroom] is None

    def who_at(self, day: str, hour: int, classroom: str) -> Optional[int]:
        """
        Get the meeting ID at a specific position.
        
        Args:
            day: Day string
            hour: Hour integer
            classroom: Classroom code string
            
        Returns:
            Meeting ID if position is occupied, None if empty
        """
        self._check_pos(day, hour, classroom)
        return self.occupancy[(day, hour)][classroom]

    def get_position(self, meeting_id: int) -> Optional[Tuple[str, int, str]]:
        """
        Get the position of a specific meeting.
        
        Args:
            meeting_id: ID of the meeting to locate
            
        Returns:
            (day, hour, classroom) tuple if meeting is placed, None otherwise
        """
        return self.where_is.get(meeting_id)

    # ---------- Mutation Methods ----------
    def place(self, meeting_id: int, day: str, hour: int, classroom: str) -> bool:
        """
        Place a meeting at the specified position.
        If the meeting was already placed elsewhere, it will be moved.
        
        Args:
            meeting_id: ID of meeting to place
            day: Target day
            hour: Target hour
            classroom: Target classroom
            
        Returns:
            True if placement succeeded, False if position is already occupied
        """
        self._check_pos(day, hour, classroom)
        
        # Check if new position is available
        if self.occupancy[(day, hour)][classroom] is not None:
            return False
        
        # Remove meeting from old position if it exists
        old = self.where_is.get(meeting_id)
        if old is not None:
            oday, ohour, oroom = old
            self.occupancy[(oday, ohour)][oroom] = None
        
        # Place meeting in new position
        self.occupancy[(day, hour)][classroom] = meeting_id
        self.where_is[meeting_id] = (day, hour, classroom)
        return True

    def remove(self, day: str, hour: int, classroom: str) -> Optional[int]:
        """
        Remove whatever meeting is at the specified position.
        
        Args:
            day: Day string
            hour: Hour integer
            classroom: Classroom code string
            
        Returns:
            Meeting ID that was removed, or None if position was already empty
        """
        self._check_pos(day, hour, classroom)

        mid = self.occupancy[(day, hour)][classroom]
        if mid is None:
            return None

        # Clear the position and remove from tracking
        self.occupancy[(day, hour)][classroom] = None
        self.where_is.pop(mid, None)
        return mid

    def move(self, src: Tuple[str, int, str], dst: Tuple[str, int, str]) -> bool:
        """
        Move a meeting from source position to destination position.
        
        Args:
            src: Source (day, hour, classroom) tuple
            dst: Destination (day, hour, classroom) tuple
            
        Returns:
            True if move succeeded, False if source is empty or destination is occupied
        """
        sday, shour, sroom = src
        dday, dhour, droom = dst
        self._check_pos(sday, shour, sroom)
        self._check_pos(dday, dhour, droom)

        # Check if source has a meeting and destination is empty
        mid = self.occupancy[(sday, shour)][sroom]
        if mid is None:
            return False
        if self.occupancy[(dday, dhour)][droom] is not None:
            return False

        # Perform the move operation
        self.occupancy[(sday, shour)][sroom] = None
        self.occupancy[(dday, dhour)][droom] = mid
        self.where_is[mid] = (dday, dhour, droom)
        return True

    def swap(self, a: Tuple[str, int, str], b: Tuple[str, int, str]) -> bool:
        """
        Swap the contents of two positions.
        Can handle empty positions and occupied positions.
        
        Args:
            a: First position (day, hour, classroom) tuple
            b: Second position (day, hour, classroom) tuple
            
        Returns:
            True (swap operation always succeeds)
        """
        aday, ahour, aroom = a
        bday, bhour, broom = b
        self._check_pos(aday, ahour, aroom)
        self._check_pos(bday, bhour, broom)

        # Get current occupants
        amid = self.occupancy[(aday, ahour)][aroom]
        bmid = self.occupancy[(bday, bhour)][broom]

        # Perform the swap
        self.occupancy[(aday, ahour)][aroom] = bmid
        self.occupancy[(bday, bhour)][broom] = amid

        # Update position tracking for non-None meetings
        if amid is not None:
            self.where_is[amid] = (bday, bhour, broom)
        
        if bmid is not None:
            self.where_is[bmid] = (aday, ahour, aroom)

        return True

    # ---------- Helper Methods ----------
    def all_free_positions(self) -> List[Tuple[str, int, str]]:
        """
        Get all empty positions in the schedule.
        
        Returns:
            List of (day, hour, classroom) tuples for all empty positions
        """
        free: List[Tuple[str, int, str]] = []
        for d in self.days:
            for h in self.hours:
                row = self.occupancy[(d, h)]
                for room, mid in row.items():
                    if mid is None:
                        free.append((d, h, room))
        return free

    def iter_assignments(self) -> List[Tuple[int, str, int, str]]:
        """
        Get all current meeting assignments.
        
        Returns:
            List of (meeting_id, day, hour, classroom) tuples for all placed meetings
        """
        return [(mid, d, h, r) for mid, (d, h, r) in self.where_is.items()]

    def print_schedule_table(self, registry: 'Registry') -> None:
        """
        Print a visual table representation of the schedule.
        Shows days as columns, hours as rows, and course codes in each slot.
        
        Args:
            registry: Registry instance to access meeting details
        """
        print("\n" + "="*100)
        print("SCHEDULE TABLE")
        print("="*100)
        
        # Header: Days
        header = "Hour |"
        for day in self.days:
            header += f" {day.name:<18} |"
        print(header)
        print("-" * len(header))
        
        # Rows: Hours
        for hour in self.hours:
            row = f"{hour:4} |"
            for day in self.days:
                slot_content = ""
                room_contents = []
                for room in self.classroom_codes:
                    mid = self.occupancy[(day, hour)].get(room)
                    if mid is not None:
                        course_code = registry.meetings[mid].course_code
                        room_contents.append(f"{room}:{course_code}")
                if room_contents:
                    slot_content = ", ".join(room_contents)
                else:
                    slot_content = "Empty"
                row += f" {slot_content:<18} |"
            print(row)
        
        print("="*100)

# ---------- Visualization Methods ----------
    def display(self, registry: Optional['Registry'] = None) -> None:
        """
        Display the schedule as a formatted timetable grid.
        
        Args:
            registry: Optional Registry to show course names instead of meeting IDs
        """
        print("\n" + "=" * 120)
        print("SCHEDULE VISUALIZATION")
        print("=" * 120)
        
        # Header: Days
        header = f"{'Hour':<8}"
        for day in self.days:
            header += f"| {str(day):<20} "
        print(header)
        print("-" * 120)
        
        # Rows: Hours
        for hour in self.hours:
            row = f"{hour:02d}:00   "
            
            for day in self.days:
                # Get all meetings at this time across all rooms
                meetings_at_time = []
                for room in self.classroom_codes:
                    mid = self.who_at(day, hour, room)
                    if mid is not None:
                        if registry:
                            meeting = registry.meetings[mid]
                            course_code = meeting.course_code
                            meetings_at_time.append(f"{course_code}@{room}")
                        else:
                            meetings_at_time.append(f"M{mid}@{room}")
                
                # Format cell content
                if meetings_at_time:
                    cell = ", ".join(meetings_at_time[:2])  # Show max 2 meetings
                    if len(meetings_at_time) > 2:
                        cell += f" +{len(meetings_at_time)-2}"
                else:
                    cell = "-"
                
                row += f"| {cell:<20} "
            
            print(row)
        
        print("=" * 120)
        
        # Summary statistics
        total_slots = len(self.days) * len(self.hours) * len(self.classroom_codes)
        occupied_slots = len(self.where_is)
        print(f"\nSummary: {occupied_slots}/{total_slots} slots occupied ({occupied_slots/total_slots*100:.1f}%)")
        print(f"Total meetings placed: {occupied_slots}")
        print()
        
    @staticmethod
    def random_initial_assignment(registry: 'Registry') -> 'Schedule':
        """
        Generate a completely random initial schedule without constraint checking.
        Places all meetings randomly into available positions.
        This can create invalid schedules with conflicts, useful for testing optimization algorithms.
        
        Args:
            registry: Registry containing meetings, classrooms, and constraints
            
        Returns:
            Schedule with all meetings randomly placed (may be invalid)
        """
        # Define schedule dimensions
        days = list(DAY)
        hours = list(range(7, 18))  # 7 AM to 5 PM
        classroom_codes = list(registry.classrooms.keys())
        
        schedule = Schedule(days, hours, classroom_codes)
        meetings = list(registry.meetings.keys())
        free_positions = schedule.all_free_positions()
        random.shuffle(free_positions)
        
        for mid, pos in zip(meetings, free_positions):
            d, h, r = pos
            schedule.place(mid, d, h, r)
        
        return schedule
