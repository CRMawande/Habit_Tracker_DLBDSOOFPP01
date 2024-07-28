# Habit Tracker App

The Habit Tracker App is a user-centric tool designed to help users create, manage, and analyze their personal habits. 
Developed using Python and SQLite, the app features a user-friendly Command Line Interface (CLI) powered by the `rich` library and `pypiglet` for banners.

## Features

- **User Management**: Register, log in, and manage user profiles.
- **Habit Creation**: Define and create new habits.
- **Habit Logging**: Track progress by logging habit completions and viewing history.
- **Analytics**: Analyze habit performance, including streak tracking and completion rates.

## Getting Started

Follow these instructions to set up and run the Habit Tracker App on your local machine.

### Prerequisites

- Python 3.7 or later
- SQLite

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/CRMawande/Habit_Tracker_DLBDSOOFPP01.git
    cd Habit_Tracker_DLBDSOOFPP01
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Usage

1. Initialize the database:
    ```sh
    python habit_tracker/storage/db_manager.py
    ```

2. Run the application:
    ```sh
    python habit_tracker/app/main.py
    ```

### Project Structure

- `habit_tracker/app/main.py`: Entry point for the application.
- `habit_tracker/app/user.py`: Manages user-related functionalities.
- `habit_tracker/app/habit.py`: Manages habit-related functionalities.
- `habit_tracker/app/analytics.py`: Provides habit analysis functionalities.
- `habit_tracker/storage/db_manager.py`: Handles database connections and CRUD operations.
- `habit_tracker/storage/ex_data.py`: Contains example data for testing.
- `habit_tracker/tests/test_habit.py`: Unit tests for habit functionalities.
- `habit_tracker/tests/test_user.py`: Unit tests for user functionalities.
- `habit_tracker/tests/test_analytics.py`: Unit tests for analytics functionalities.
- `habit_tracker/tests/test_db_manager.py`: Unit tests for database manager functionalities.

### Command Line Interface (CLI)

The CLI provides an intuitive way for users to interact with the Habit Tracker App. Upon running the application, users will be presented with a main menu offering options to register, log in, and exit. Once logged in, users can navigate through various functionalities, including:

- **Dashboard**: View a summary of their habits and current status.
- **Habit Management**: Create, update, delete, activate, and deactivate habits.
- **Logging**: Add entries to track the completion of habits.
- **Analytics**: View detailed analysis of habit performance, including longest streaks and completion rates.
- **Profile Management**: Update user information and log out.

All interactions are displayed with rich formatting and banners for an enhanced user experience.

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contact

For any inquiries or feedback, please contact [charmaine.mawande@iu-study.org](mailto:charmaine.mawande@iu-study.org).

