from storage.db_manager import (
    create_habit, get_habits_by_user, update_habit, delete_habit, add_log_entry,
    count_success_by_habit, count_consecutive_incomplete, get_last_log_entry
)
from datetime import datetime, timedelta


class Habit:
    def __init__(self, habit_id, user_id, name, description, periodicity, duration, deadline, created_at, active=1,
                 streak=0):
        # Initialize a Habit instance with default values
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

    @staticmethod
    def calculate_deadline(periodicity, duration, created_at=None):
        # Calculate the deadline based on periodicity and duration
        now = created_at if created_at else datetime.now()
        if periodicity == "daily":
            return now + timedelta(days=1 * duration)  # Daily deadline
        elif periodicity == "weekly":
            return now + timedelta(days=7 * duration)  # Weekly deadline
        return now  # Default to now if no periodicity

    def add_log_entry(self, success, note, log_time=None):
        # Add a log entry for the habit
        log_time = log_time if log_time else datetime.now()  # Use current time if not provided
        log_id = add_log_entry(self.habit_id, success, note, log_time=log_time)  # Store log entry in database
        print(f"Log entry added for habit_id {self.habit_id}: success={success}, note={note}")
        return log_id

    @staticmethod
    def create(user_id, name, description, periodicity, duration, streak=None, created_at=None):
        # Create a new habit and store it in the database
        created_at = created_at or datetime.now()  # Use current time if not provided
        deadline = Habit.calculate_deadline(periodicity, duration, created_at)  # Calculate deadline
        active = 1
        streak = streak or 0
        habit_id = create_habit(user_id, name, description, periodicity, duration, active=active, deadline=deadline,
                                streak=streak, created_at=created_at)  # Store habit and get habit_id
        habit = Habit(habit_id, user_id, name, description, periodicity, duration, deadline=deadline, streak=streak,
                      created_at=created_at)
        habit.add_log_entry(success=1, note="Habit created and activated", log_time=created_at)  # Log creation
        print(f"Habit created: {habit}")
        return habit

    @staticmethod
    def get_all_by_user(user_id):
        # Retrieve all habits for a specific user
        habits_data = get_habits_by_user(user_id)  # Fetch habits from database
        habits = []
        for habit_data in habits_data:
            habit = Habit(*habit_data)  # Create Habit instances from data
            habits.append(habit)
        print(f"Retrieved {len(habits)} habits for user_id {user_id}")
        return habits

    def update(self, name=None, description=None, periodicity=None, duration=None, active=1):
        # Update habit details and log the update
        if name:
            self.name = name
        if description:
            self.description = description
        if periodicity:
            self.periodicity = periodicity
        if duration is not None:
            self.duration = duration
        if self.deadline:
            self.deadline = Habit.calculate_deadline(periodicity, duration, datetime.now())  # Recalculate deadline

        update_habit(self.habit_id, name, description, periodicity, duration, active, deadline=self.deadline)
        # Update habit in database
        self.add_log_entry(success=1, note="Habit restarted and activated")  # Log update
        print(f"Habit updated: {self}")

    def delete(self):
        # Delete the habit from the database
        delete_habit(self.habit_id)  # Remove habit from database
        self.add_log_entry(success=0, note="Habit deleted")  # Log deletion
        print(f"Habit deleted: {self.habit_id}")

    def can_mark_complete(self):
        # Determine if the habit can be marked as complete based on its periodicity
        last_log = get_last_log_entry(self.habit_id)  # Fetch last log entry
        if not last_log:
            return True  # No log entry found, can mark as complete

        last_log_time = datetime.strptime(last_log['log_time'], '%Y-%m-%d %H:%M:%S.%f').timestamp()
        now = datetime.now().timestamp()

        if self.periodicity == 'daily' and self.streak != 0:
            return (now - last_log_time) >= 86400  # Check daily periodicity (86400 seconds in a day)
        elif self.periodicity == 'weekly' and self.streak != 0:
            return (now - last_log_time) >= 604800  # Check weekly periodicity (604800 seconds in a week)

        return True  # Default to allow marking as complete

    def update_status(self):
        # Update the habit status and log the result
        if not self.active:
            self.add_log_entry(success=0, note="Habit update failed - habit inactive")  # Log failure
            print(f"Failed to update status for inactive habit: {self.habit_id}")
            return

        current_time = datetime.now().timestamp()
        deadline_time = self.deadline.timestamp()

        if current_time > deadline_time:
            self.add_log_entry(success=0, note="Habit marked as incomplete")  # Log incomplete status
            self.streak = Habit.calculate_streak(self.habit_id)  # Recalculate streak
        else:
            if self.can_mark_complete():
                self.add_log_entry(success=1, note="Habit completed successfully on time")  # Log successful completion
                self.streak = Habit.calculate_streak(self.habit_id)  # Recalculate streak
                print(f"Habit '{self.name}' marked as complete. Streak: {self.streak}")
            else:
                print(f"Habit '{self.name}' cannot be marked as complete yet. Please wait until the next period.")

    def deactivate(self):
        # Deactivate the habit if its deadline has passed
        current_time = int(datetime.now().timestamp())
        deadline_time = int(self.deadline.timestamp())
        if self.active and deadline_time < current_time:
            self.active = 0
            update_habit(self.habit_id, active=0)  # Update active status in database
            self.add_log_entry(success=0, note="Habit deactivated - deadline exceeded")  # Log deactivation
            print(f"Habit '{self.name}' deactivated due to deadline exceedance.")
        elif self.active and deadline_time > current_time:
            print(f"Habit '{self.name}' is not overdue yet")
        else:
            print(f"Habit '{self.name}' is already deactivated")

    @staticmethod
    def calculate_streak(habit_id):
        # Calculate and update the streak for a specific habit
        success_count = count_success_by_habit(habit_id)  # Count successful logs
        consecutive_incomplete = count_consecutive_incomplete(habit_id)  # Count consecutive incomplete logs

        if success_count > 0 and consecutive_incomplete < 3:
            new_streak = success_count  # Set streak based on success count
        else:
            new_streak = 0  # Reset streak if conditions are not met

        update_habit(habit_id, streak=new_streak)  # Update streak in database
        print(f"Calculated streak for habit_id {habit_id}: {new_streak}")
        return new_streak
