from datetime import datetime
from rich.table import Table
from app.analytics import get_active_habits, get_habits_by_periodicity, get_longest_streak_all_habits, \
    get_completion_rate, analyze_logs
from app.habit import Habit
from app.user import User
from storage.db_manager import get_habit_by_id
import pyfiglet
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

console = Console()


def main_menu():
    ascii_banner = pyfiglet.figlet_format("""
    Welcome to the
      Habit Tracker
    """)
    console.print(Text(ascii_banner, style="cyan"))
    console.print("\nUnlock your potential by building healthy habits. Log in or register to start your journey today!")
    console.print("1. Register New User")
    console.print("2. Log In")
    console.print("3. How to Use")
    console.print("4. Exit")

    while True:
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="4").strip()

        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            how_to_use()
        elif choice == '4':
            console.print("Exiting application...")
            exit(0)  # Terminate the application
        else:
            console.print("[bold red]Invalid choice. Please select a valid option.[/bold red]")


def how_to_use():
    console.print("[bold green]How to Use the Habit Tracker App:[/bold green]\n")

    console.print("[bold]1. Register New User[/bold]")
    console.print("   - Choose this option to create a new user account.")
    console.print("   - You will be asked to provide a username and password.")

    console.print("[bold]2. Log In[/bold]")
    console.print("   - Choose this option to log into your existing account.")
    console.print("   - Enter your username and password to access your dashboard.")

    console.print("[bold]3. Dashboard[/bold]")
    console.print("   - After logging in, you will be taken to your dashboard.")
    console.print("   - From here, you can manage habits, view analytics, and update your profile.")

    console.print("[bold]4. Profile Management[/bold]")
    console.print("   - Update your username or password, or delete your account.")
    console.print("   - This is where you can make changes to your profile.")

    console.print("[bold]5. Analytics[/bold]")
    console.print("   - View various statistics about your habits.")
    console.print(
        "   - Options include viewing habits by periodicity, longest streaks, completion rates, and log analysis.")
    console.print("[bold]6. Managing Habits[/bold]")
    console.print("   - [bold]Mark Daily/Weekly Habits[/bold]:")
    console.print("     - Mark habits as completed daily or weekly to increase your streak.")
    console.print("   - [bold]Check Deadlines[/bold]:")
    console.print("     - Review upcoming deadlines for your habits.")
    console.print("   - [bold]Deactivate Overdue Habits[/bold]:")
    console.print("     - Deactivate habits past their deadlines to stop tracking them.")
    console.print("   - [bold]Activate Existing Habits[/bold]:")
    console.print("     - Reactivate habits to set a new deadline and continue tracking streaks.")
    console.print("   - [bold]Delete Habits[/bold]:")
    console.print("     - Permanently remove habits you no longer want to track.")
    console.print("   - [bold]Update Habits[/bold]:")
    console.print("     - Modify habit details, such as name, description, periodicity, or duration.")

    console.print("[bold]7. Exiting the Application[/bold]")
    console.print("   - Choose 'Exit' from the main menu to close the application.")

    console.print("[bold green]Press any key to return to the Main Menu...[/bold green]")
    Prompt.ask("")
    main_menu()


def login():
    console.print("\nLogin")
    username = Prompt.ask("Enter username")
    user = User.get_by_username(username)

    if not user:
        console.print("Username not found. Please check your username and try again.")
        main_menu()
        return

    if user:
        attempts = 3
        while attempts > 0:
            password = Prompt.ask("Enter password")
            if user.check_password(password):
                user.update_last_login()
                console.print(f"Welcome back, {user.username}! Your user ID is {user.user_id}."
                              f" Redirecting to the Dashboard...\n")
                dashboard(user)
                return
            else:
                attempts -= 1
                console.print(f"Incorrect password. You have {attempts} attempts left.")

        console.print("Too many unsuccessful attempts.")
        recover_choice = Prompt.ask("Did you forget your password? Would you like to recover it? (yes/no)",
                                    choices=["yes", "no"], default="no")
        if recover_choice == 'yes':
            forgot_password()
        else:
            console.print("Returning to the main menu.\n")
            main_menu()
    else:
        console.print("Username not found. Please try again.\n")
        main_menu()


def forgot_password():
    console.print("\nForgot Password")
    username = Prompt.ask("Enter username")
    user_id = Prompt.ask("Enter user ID")

    user = User.get_by_username(username)

    if user and str(user.user_id) == user_id:
        new_password = Prompt.ask("Enter new password")
        user.reset_password(new_password)
        console.print("Password reset successfully. Logging you in...")
        user.update_last_login()
        console.print(f"Welcome back, {user.username}! Your user ID is {user.user_id}."
                      f" Redirecting to the Dashboard...\n")
        dashboard(user)
    else:
        console.print("Invalid username or user ID. Please try again.")
        main_menu()


def register():
    console.print("\nRegister as a new user")
    username = Prompt.ask("Enter username")
    password = Prompt.ask("Enter password")
    confirm_password = Prompt.ask("Confirm password")

    if password != confirm_password:
        console.print("Passwords do not match. Please try again.\n")
        register()
        return

    created_at = datetime.now().isoformat()  # or however you manage timestamps in your application

    try:
        user = User.create(username, password, created_at)
        console.print(f"Welcome {user.username}! Registration successful. Your user ID is {user.user_id}."
                      f" Redirecting to the Dashboard...\n")
        # Placeholder for redirecting to the Dashboard
        dashboard(user)
    except Exception as e:
        console.print(f"Registration failed: {str(e)}. Please try again.\n")
        register()


def dashboard(user):
    now = datetime.now().strftime("%d %B %Y")
    console.print(f"Today's date is [bold cyan]{now}[/bold cyan]!")
    console.print("Remember to mark your habits to maintain your streak!")

    while True:
        active_habits = get_active_habits(user.user_id)

        if active_habits:
            table = Table(title="Your Active Habits")
            table.add_column("Habit Name", style="cyan", no_wrap=True)
            table.add_column("Deadline", style="magenta")
            table.add_column("Streak", style="green")

            for habit in active_habits:
                table.add_row(habit['name'], habit['deadline'], str(habit['streak']))

            console.print(table)
        else:
            console.print("You have no active habits.")

        console.print("\nWhat would you like to do today?")
        console.print("1. Create a Habit")
        console.print("2. Habit Status Management")
        console.print("3. Profile Management")
        console.print("4. Analytics")
        console.print("5. Log out")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"], default="1").strip()

        if choice == '1':
            create_habit(user)
        elif choice == '2':
            habit_status_management(user)
        elif choice == '3':
            profile_management(user)
        elif choice == '4':
            analytics(user)
        elif choice == '5':
            log_out(user)
        else:
            console.print("Invalid choice. Please try again.")


def create_habit(user):
    console.print("Create a Habit")

    while True:
        name = Prompt.ask("Enter habit name").strip().capitalize()
        if name:
            break
        else:
            console.print("Habit name cannot be empty. Please enter a valid name.")

    while True:
        description = Prompt.ask("Enter habit description").strip().capitalize()
        if description:
            break
        else:
            console.print("Habit description cannot be empty. Please enter a valid description.")

    while True:
        periodicity = Prompt.ask("Select periodicity (daily/weekly)", choices=["daily", "weekly"],
                                 default="daily").strip().lower()
        if periodicity in ['daily', 'weekly']:
            break
        else:
            console.print("Invalid periodicity. Please enter 'daily' or 'weekly'.")

    while True:
        try:
            duration = int(Prompt.ask("Enter duration (number of days/weeks) must be more than 0").strip())
            break
        except ValueError:
            console.print("Invalid duration. Please enter a valid number.")

    try:
        habit = Habit.create(user.user_id, name, description, periodicity, duration)
        console.print(
            f"Your [bold cyan]{periodicity}[/bold cyan] habit"
            f" '[bold]{name}[/bold]' has been created and activated. Your deadline is {habit.deadline}.")
    except Exception as e:
        console.print(f"Failed to create habit: [red]{str(e)}[/red]")


def habit_status_management(user):
    console.print("\nHabit Status Management:")
    console.print("1. Mark Habit Complete")
    console.print("2. Deactivate Overdue Habits")
    console.print("3. Activate Existing Habit")
    console.print("4. Delete a Habit")
    console.print("5. Back to Dashboard")

    choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"], default="5").strip()

    if choice == "1":
        mark_habit_complete(user)
    elif choice == "2":
        deactivate_habits(user)
    elif choice == '3':
        update_habit(user)
    elif choice == '4':
        delete_habit(user)
    elif choice == '5':
        return
    else:
        console.print("Invalid choice. Please try again.")
        habit_status_management(user)


def mark_habit_complete(user):
    habits = get_active_habits_with_names(user.user_id)
    if not habits:
        console.print("No active habits found.")
        return

    table = Table(title="Active Habits")
    table.add_column("Habit ID", style="cyan")
    table.add_column("Habit Name", style="magenta")

    for habit_id, name in habits.items():
        table.add_row(str(habit_id), name)

    console.print(table)

    try:
        selected_id = int(Prompt.ask("Enter the number of the habit to update status").strip())

        if selected_id in habits:
            habit = get_habit_by_id(selected_id)
            if habit:
                habit.update_status()
                console.print(f"Habit '{habits[selected_id]}' status updated.")
            else:
                console.print(f"Habit with ID '{selected_id}' not found.")
        else:
            console.print(f"Habit with ID '{selected_id}' not found.")
    except ValueError:
        console.print("Invalid input. Please enter a valid habit number.")

    next_step = Prompt.ask(
        "Enter '1' to Continue or '2' to return to Habit Status Management menu  ",
        choices=["1", "2"], default="2")
    if next_step == '1':
        mark_habit_complete(user)
    elif next_step == '2':
        habit_status_management(user)


def deactivate_habits(user):
    habits = get_active_habits_with_names(user.user_id)
    if not habits:
        console.print("No active habits found.")
        return

    table = Table(title="Active Habits")
    table.add_column("Habit ID", style="cyan")
    table.add_column("Habit Name", style="magenta")

    for habit_id, name in habits.items():
        table.add_row(str(habit_id), name)

    console.print(table)

    try:
        selected_id = int(Prompt.ask("Enter the number of the habit to deactivate").strip())

        habit = get_habit_by_id(selected_id)

        if habit:
            habit.deactivate()
        else:
            console.print(f"Habit with ID '{selected_id}' not found.")
    except ValueError:
        console.print("Invalid input. Please enter a valid habit number.")
        deactivate_habits(user)

    next_step = Prompt.ask(
        "Enter '1' return to Dashboard or '2' to return to Habit Status Management menu or"
        "Press any other key to Continue",
        choices=["1", "2"], default="2")
    if next_step == '1':
        dashboard(user)
    elif next_step == '2':
        habit_status_management(user)
    else:
        deactivate_habits(user)


def update_habit(user):
    console.print("\nUpdate Habit")

    habits = Habit.get_all_by_user(user.user_id)
    if not habits:
        console.print("No habits found.")
        return

    table = Table(title="Your Habits")
    table.add_column("Number", style="cyan")
    table.add_column("Habit Name", style="magenta")

    for idx, habit in enumerate(habits, start=1):
        table.add_row(str(idx), habit.name)

    console.print(table)

    while True:
        choice = Prompt.ask("Enter the number of the habit to update").strip()

        try:
            habit_to_update = habits[int(choice) - 1]
            console.print("Press enter to skip updating a detail.")

            new_name = Prompt.ask(f"Enter new habit name (current: {habit_to_update.name})",
                                  default=habit_to_update.name).strip().capitalize()
            new_description = Prompt.ask(f"Enter new habit description (current: {habit_to_update.description})",
                                         default=habit_to_update.description).strip().capitalize()
            new_periodicity = Prompt.ask(f"Enter new habit periodicity (current: {habit_to_update.periodicity})",
                                         choices=["daily", "weekly"],
                                         default=habit_to_update.periodicity).strip().lower()
            new_duration_input = Prompt.ask(f"Enter new habit duration (current: {habit_to_update.duration})"
                                            f" must be more than 0",
                                            default=habit_to_update.duration)

            new_duration = int(new_duration_input.strip()) if new_duration_input.strip() else habit_to_update.duration

            habit_to_update.update(name=new_name, description=new_description, periodicity=new_periodicity,
                                   duration=new_duration)
            console.print(f"Habit '{new_name}' updated successfully.")
            break
        except (IndexError, ValueError) as e:
            console.print(f"Invalid choice or input. Please try again. Error: {str(e)}")
        except Exception as e:
            console.print(f"Failed to update habit: {str(e)}")


def delete_habit(user):
    console.print("\nDelete Habit")

    habits = Habit.get_all_by_user(user.user_id)
    if not habits:
        console.print("No habits found.")
        return

    table = Table(title="Your Habits")
    table.add_column("Number", style="cyan")
    table.add_column("Habit Name", style="magenta")

    for idx, habit in enumerate(habits, start=1):
        table.add_row(str(idx), habit.name)

    console.print(table)

    while True:
        choice = Prompt.ask("Enter the number of the habit to delete").strip()

        try:
            habit_to_delete = habits[int(choice) - 1]
            confirmation = Prompt.ask(
                f"Are you sure you want to delete the habit '{habit_to_delete.name}'? This action cannot be undone.",
                choices=["yes", "no"], default="no")
            if confirmation.lower() == 'yes':
                habit_to_delete.delete()
                console.print(f"Habit '{habit_to_delete.name}' deleted successfully.")
            else:
                console.print("Deletion cancelled.")
        except (IndexError, ValueError):
            console.print("Invalid choice. Please enter a valid number.")
        except Exception as e:
            console.print(f"Failed to delete habit: {str(e)}")

        next_step = Prompt.ask(
            "Enter '1' return to Dashboard or '2' to return to Habit Status Management menu or"
            "Press any other key to Continue",
            choices=["1", "2"], default="2")
        if next_step == '1':
            dashboard(user)
        elif next_step == '2':
            habit_status_management(user)
        else:
            break


def profile_management(user):
    while True:
        console.print("\nProfile Management:")
        console.print("1. Update Profile")
        console.print("2. Delete Profile")
        console.print("3. Back to Dashboard")

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"], default="3").strip()

        if choice == '1':
            console.print("Enter new details. Press Enter to keep the current value.")
            new_username = Prompt.ask(f"New username (current: {user.username})", default=user.username)
            new_password = Prompt.ask("New password", password=True)

            if new_username.strip():
                user.username = new_username
            if new_password.strip():
                user.password = new_password

            user.update()
            console.print("Profile updated successfully! Redirecting to Profile Management...")

        elif choice == '2':
            while True:
                confirmation = Prompt.ask(
                    "Are you sure you want to delete your profile? This action cannot be undone. (yes/no)",
                    choices=["yes", "no"], default="no")
                if confirmation.lower() == 'yes':
                    user.delete()
                    console.print("Profile deleted successfully. Exiting application...")
                    main_menu()
                elif confirmation.lower() == 'no':
                    console.print("Returning to Profile Management...")
                    break
                else:
                    console.print("Invalid input. Please enter 'yes' or 'no'.")

        elif choice == '3':
            console.print("Returning to the Dashboard...")
            break

        else:
            console.print("Invalid choice. Please select a valid option.")


def analytics(user):
    def analytics_menu():
        while True:
            console.print("\n[bold green]Analytics Menu:[/bold green]")
            console.print("1. View Habits by Periodicity")
            console.print("2. View Longest Streak for All Habits")
            console.print("3. View Longest Streak for a Habit")
            console.print("4. View Completion Rate for a Habit")
            console.print("5. Analyze Logs for a Habit")
            console.print("6. Back to Dashboard")

            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6"], default="6").strip()

            if choice == '1':
                view_habits_by_periodicity(user)
            elif choice == '2':
                view_longest_streak_all_habits(user)
            elif choice == '3':
                view_longest_streak_for_habit(user)
            elif choice == '4':
                view_completion_rate_for_habit(user)
            elif choice == '5':
                analyze_logs_for_habit(user)
            elif choice == '6':
                console.log("Returning to dashboard.")
                dashboard(user)
                break
            else:
                console.log("[bold red]Invalid choice. Please enter a number between 1 and 6.[/bold red]")

    console.log("Entering analytics menu.")
    analytics_menu()


def view_habits_by_periodicity(user):
    while True:
        periodicity = Prompt.ask("Enter periodicity (daily, weekly)", choices=["daily", "weekly"]).strip().lower()
        habits_by_periodicity = get_habits_by_periodicity(user.user_id, periodicity)

        if habits_by_periodicity:
            console.print(f"\nHabits with periodicity '{periodicity}':")
            for habit in habits_by_periodicity:
                console.print(f"- {habit['name']}")
        else:
            console.print(f"No habits found with periodicity '{periodicity}'.")

        handle_return_option(user, view_habits_by_periodicity)


def view_longest_streak_all_habits(user):
    longest_streak_habit = get_longest_streak_all_habits(user.user_id)

    if longest_streak_habit:
        habit_name = longest_streak_habit['name']
        longest_streak = longest_streak_habit['streak']
        periodicity = longest_streak_habit['periodicity']

        streak_text = f"{longest_streak} day(s)" if periodicity == 'daily' else f"{longest_streak} week(s)"
        console.print(f"\nLongest streak across all habits is for habit '{habit_name}' with a streak of {streak_text}.")
    else:
        console.print("No streak information found.")

    handle_return_option(user, view_longest_streak_all_habits)


def view_longest_streak_for_habit(user):
    habits = get_active_habits_with_names(user.user_id)

    if not habits:
        console.print("No active habits found.")
        return

    console.print("\nActive Habits with Longest Streaks:")
    for habit_id, name in habits.items():
        habit = get_habit_by_id(habit_id)
        if habit:
            longest_streak = habit.streak
            periodicity = habit.periodicity

            streak_text = f"{longest_streak} day(s)" if periodicity == 'daily' else f"{longest_streak} week(s)"
            console.print(f"- {name}: {streak_text}")
        else:
            console.print(f"- {name}: No streak found")

    handle_return_option(user, view_longest_streak_for_habit)


def view_completion_rate_for_habit(user):
    habits = get_active_habits_with_names(user.user_id)

    if not habits:
        console.print("No active habits found.")
        return

    console.print("\nActive Habits:")
    for habit_id, name in habits.items():
        console.print(f"{habit_id}. {name}")

    try:
        selected_id = int(Prompt.ask("Enter the number of the habit to view completion rate").strip())

        if selected_id in habits:
            completion_rate = get_completion_rate(selected_id)
            name = habits[selected_id]
            if completion_rate is not None:
                console.print(f"Completion rate for habit '{name}': {completion_rate}%.")
            else:
                console.print(f"No completion rate found for habit '{name}'.")
        else:
            console.print(f"Habit with ID '{selected_id}' not found.")
    except ValueError:
        console.print("Invalid input. Please enter a valid habit number.")

    handle_return_option(user, view_completion_rate_for_habit)


def analyze_logs_for_habit(user):
    habits = get_active_habits_with_names(user.user_id)

    if not habits:
        console.print("No active habits found.")
        return

    console.print("\nActive Habits:")
    for habit_id, name in habits.items():
        console.print(f"{habit_id}. {name}")

    try:
        selected_id = int(Prompt.ask("Enter the number of the habit to analyze logs").strip())

        if selected_id in habits:
            log_analysis = analyze_logs(selected_id)
            name = habits[selected_id]
            if log_analysis:
                console.print(f"\nLog analysis for habit '{name}':")
                console.print(f"Total logs: {log_analysis['total_logs']}")
                console.print(f"Success logs: {log_analysis['success_logs']}")
                console.print(f"Failure logs: {log_analysis['failure_logs']}")
                console.print(f"Completed Log habits: {log_analysis['completed_habits']}")
                console.print(f"Incomplete Log habits: {log_analysis['failure_habits']}")
                console.print("Distinct Notes:")
                for note in log_analysis['notes']:
                    console.print(f"- {note}")
            else:
                console.print(f"No log analysis found for habit '{name}'.")
        else:
            console.print(f"Habit with ID '{selected_id}' not found.")
    except ValueError:
        console.print("Invalid input. Please enter a valid habit number.")

    handle_return_option(user, analyze_logs_for_habit)


# Helper Function
def get_active_habits_with_names(user_id):
    habits_data = get_active_habits(user_id)
    return {habit['habit_id']: habit['name'] for habit in habits_data}


# Helper Function
def handle_return_option(user, current_function):
    next_step = Prompt.ask(
        "\nEnter '1' to return to Analytics menu or '2' to return to Dashboard or '3' to make another analysis",
        choices=["1", "2", "3"], default="2").strip()

    if next_step == '1':
        analytics(user)
    elif next_step == '2':
        dashboard(user)
    elif next_step == '3':
        current_function(user)
    else:
        console.print("Invalid choice. Choose 1, 2, or 3.")
        handle_return_option(user, current_function)


def log_out(user):
    while True:
        confirmation = Prompt.ask("Are you sure you want to log out? (yes/no)", choices=["yes", "no"], default="no")
        if confirmation.lower() == 'yes':
            console.print("You have been logged out.")
            main_menu()
        elif confirmation.lower() == 'no':
            console.print("Returning to the Dashboard...")
            dashboard(user)
            return
        else:
            console.print("Invalid input. Please enter 'yes' or 'no'.")


if __name__ == "__main__":
    main_menu()
