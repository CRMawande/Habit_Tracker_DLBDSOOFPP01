from storage.db_manager import (
    create_habit, get_habits_by_user, update_habit, delete_habit, add_log_entry,
    count_success_by_habit, count_consecutive_incomplete, get_last_log_entry
)
from datetime import datetime, timedelta


class Habit:
    def __init__(self, habit_id, user_id, name, description, periodicity, duration, deadline, created_at, active=1,
                 streak=0):
        self.habit_id = habit_id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.duration = duration
        self.active = active
        self.deadline = deadline
        self.streak = streak
        self.created_at = created_at

    # Helper Function
    @staticmethod
    def calculate_deadline(periodicity, duration, created_at=None):
        now = created_at if created_at else datetime.now()
        if periodicity == "daily":
            return now + timedelta(days=1 * duration)
        elif periodicity == "weekly":
            return now + timedelta(days=7 * duration)
        return now

    def add_log_entry(self, success, note, log_time=None):
        log_time = log_time if log_time else datetime.now()
        log_id = add_log_entry(self.habit_id, success, note, log_time=log_time)
        print(f"Log entry added for habit_id {self.habit_id}: success={success}, note={note}")
        return log_id

    @staticmethod
    def create(user_id, name, description, periodicity, duration, streak=None, created_at=None):
        created_at = created_at or datetime.now()
        deadline = Habit.calculate_deadline(periodicity, duration, created_at)
        active = 1
        streak = streak or 0
        habit_id = create_habit(user_id, name, description, periodicity, duration, active=active, deadline=deadline,
                                streak=streak, created_at=created_at)
        habit = Habit(habit_id, user_id, name, description, periodicity, duration, deadline=deadline, streak=streak,
                      created_at=created_at)
        habit.add_log_entry(success=1, note="Habit created and activated", log_time=created_at)
        print(f"Habit created: {habit}")
        return habit

    @staticmethod
    def get_all_by_user(user_id):
        habits_data = get_habits_by_user(user_id)
        habits = []
        for habit_data in habits_data:
            habit = Habit(*habit_data)
            habits.append(habit)
        print(f"Retrieved {len(habits)} habits for user_id {user_id}")
        return habits

    def update(self, name=None, description=None, periodicity=None, duration=None, active=1):
        if name:
            self.name = name
        if description:
            self.description = description
        if periodicity:
            self.periodicity = periodicity
        if duration is not None:
            self.duration = duration
        if self.deadline:
            self.deadline = Habit.calculate_deadline(periodicity, duration, datetime.now())

        update_habit(self.habit_id, name, description, periodicity, duration, active, deadline=self.deadline)
        self.add_log_entry(success=1, note="Habit restarted and activated")
        print(f"Habit updated: {self}")

    def delete(self):
        delete_habit(self.habit_id)
        self.add_log_entry(success=0, note="Habit deleted")
        print(f"Habit deleted: {self.habit_id}")

    def can_mark_complete(self):
        last_log = get_last_log_entry(self.habit_id)
        if not last_log:
            return True  # No log entry found, can mark as complete

        last_log_time = datetime.strptime(last_log['log_time'], '%Y-%m-%d %H:%M:%S.%f').timestamp()
        now = datetime.now().timestamp()

        if self.periodicity == 'daily' and self.streak != 0:
            return (now - last_log_time) >= 86400  # 86400 seconds in a day
        elif self.periodicity == 'weekly' and self.streak != 0:
            return (now - last_log_time) >= 604800  # 604800 seconds in a week

        return True  # Default to allow marking as complete

    def update_status(self):
        if not self.active:
            self.add_log_entry(success=0, note="Habit update failed - habit inactive")
            print(f"Failed to update status for inactive habit: {self.habit_id}")
            return

        current_time = datetime.now().timestamp()
        deadline_time = self.deadline.timestamp()

        if current_time > deadline_time:
            self.add_log_entry(success=0, note="Habit marked as incomplete")
            self.streak = Habit.calculate_streak(self.habit_id)
        else:
            if self.can_mark_complete():
                self.add_log_entry(success=1, note="Habit completed successfully on time")
                self.streak = Habit.calculate_streak(self.habit_id)
                print(f"Habit '{self.name}' marked as complete. Streak: {self.streak}")
            else:
                print(f"Habit '{self.name}' cannot be marked as complete yet. Please wait until the next period.")

    def deactivate(self):
        current_time = int(datetime.now().timestamp())
        deadline_time = int(self.deadline.timestamp())
        if self.active and deadline_time < current_time:
            self.active = 0
            update_habit(self.habit_id, active=0)  # Update active status in database
            self.add_log_entry(success=0, note="Habit deactivated - deadline exceeded")
            print(f"Habit '{self.name}' deactivated due to deadline exceedance.")
        elif self.active and deadline_time > current_time:
            print(f"Habit '{self.name}' is not overdue yet")
        else:
            print(f"Habit '{self.name}' is already deactivated")

    @staticmethod
    def calculate_streak(habit_id):
        """Calculate streak for a specific habit."""
        success_count = count_success_by_habit(habit_id)
        consecutive_incomplete = count_consecutive_incomplete(habit_id)

        if success_count > 0 and consecutive_incomplete < 3:
            new_streak = success_count
        else:
            new_streak = 0

        update_habit(habit_id, streak=new_streak)
        print(f"Calculated streak for habit_id {habit_id}: {new_streak}")
        return new_streak
