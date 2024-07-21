import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / 'habit_tracker.db'


def create_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DB_FILE)
    return connection


def close_connection(connection):
    """Close the database connection."""
    connection.close()


def create_tables():
    """Create necessary tables if they do not exist."""
    with create_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Habit (
            habit_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            periodicity TEXT NOT NULL,
            duration INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            deadline TIMESTAMP,
            streak INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES User (user_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Log (
            log_id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 0,
            note TEXT,
            FOREIGN KEY (habit_id) REFERENCES Habit (habit_id)
        )
        """)

    print("Tables created successfully.")


def create_user(username, password, created_at):
    sql = """
        INSERT INTO User (username, password, created_at, last_login)
        VALUES (?, ?, ?, ?)
    """
    last_login = datetime.now().isoformat()
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (username, password, created_at, last_login))
            user_id = cursor.lastrowid  # Get the last inserted ID
            print(f"New user ID: {user_id}")  # Debug print
            return user_id
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise


def get_user_by_username(username):
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM User WHERE username = ?
        """, (username,))
        return cursor.fetchone()


def update_last_login(username):
    sql = """
        UPDATE User
        SET last_login = ?
        WHERE username = ?
    """
    now = datetime.now()
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (now, username))
        conn.commit()
        print(f"Last login updated for user_id {username}.")


def update_user(user_id, username=None, password=None):
    with create_connection() as connection:
        cursor = connection.cursor()
        if username:
            cursor.execute("""
            UPDATE User SET username = ? WHERE user_id = ?
            """, (username, user_id))
        if password:
            cursor.execute("""
            UPDATE User SET password = ? WHERE user_id = ?
            """, (password, user_id))
        print(f"User with ID {user_id} updated successfully.")


def delete_user(user_id):
    """Delete a user from the database and all associated habits and logs."""
    with create_connection() as connection:
        cursor = connection.cursor()

        # Delete logs associated with the user's habits
        cursor.execute("""
        DELETE FROM Log WHERE habit_id IN (SELECT habit_id FROM Habit WHERE user_id = ?)
        """, (user_id,))

        # Delete the user's habits
        cursor.execute("""
        DELETE FROM Habit WHERE user_id = ?
        """, (user_id,))

        # Delete the user
        cursor.execute("""
        DELETE FROM User WHERE user_id = ?
        """, (user_id,))

        print(f"User with ID {user_id} and all associated habits and logs deleted successfully.")


def create_habit(user_id, name, description, periodicity, duration, active, deadline, streak, created_at):
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO Habit (user_id, name, description, periodicity, duration, active, deadline, streak, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, description, periodicity, duration, active, deadline, streak, created_at))
        print(f"Habit '{name}' created successfully.")
        return cursor.lastrowid


def get_habits_by_user(user_id):
    with create_connection() as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM Habit WHERE user_id = ?
        """, (user_id,))
        return cursor.fetchall()


def get_habit_by_id(habit_id):
    from app.habit import Habit

    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT *
        FROM Habit WHERE habit_id = ?
        """, (habit_id,))
        habit_data = cursor.fetchone()

        if habit_data:
            habit = Habit(
                habit_id=habit_data[0],
                user_id=habit_data[1],
                name=habit_data[2],
                description=habit_data[3],
                periodicity=habit_data[4],
                duration=habit_data[5],
                active=habit_data[6],
                deadline=datetime.fromisoformat(habit_data[7]),
                streak=habit_data[8],
                created_at=habit_data[9]
            )
            return habit
        return None


def update_habit(habit_id, name=None, description=None, periodicity=None, duration=None, active=None, deadline=None,
                 streak=None):
    with create_connection() as connection:
        cursor = connection.cursor()
        if name:
            cursor.execute("""
            UPDATE Habit SET name = ? WHERE habit_id = ?
            """, (name, habit_id))
        if description:
            cursor.execute("""
            UPDATE Habit SET description = ? WHERE habit_id = ?
            """, (description, habit_id))
        if periodicity:
            cursor.execute("""
            UPDATE Habit SET periodicity = ? WHERE habit_id = ?
            """, (periodicity, habit_id))
        if duration:
            cursor.execute("""
            UPDATE Habit SET duration = ? WHERE habit_id = ?
            """, (duration, habit_id))
        if active is not None:
            cursor.execute("""
            UPDATE Habit SET active = ? WHERE habit_id = ?
            """, (active, habit_id))
        if deadline:
            cursor.execute("""
            UPDATE Habit SET deadline = ? WHERE habit_id = ?
            """, (deadline, habit_id))
        if streak is not None:
            cursor.execute("""
            UPDATE Habit SET streak = ? WHERE habit_id = ?
            """, (streak, habit_id))
        print(f"Habit with ID {habit_id} updated successfully.")


def delete_habit(habit_id):
    """Delete a habit from the database and all associated logs."""
    with create_connection() as connection:
        cursor = connection.cursor()

        # Delete logs associated with the habit
        cursor.execute("""
        DELETE FROM Log WHERE habit_id = ?
        """, (habit_id,))

        # Delete the habit
        cursor.execute("""
        DELETE FROM Habit WHERE habit_id = ?
        """, (habit_id,))

        print(f"Habit with ID {habit_id} and all associated logs deleted successfully.")


def add_log_entry(habit_id, success, note, log_time):
    """Add a log entry for a habit."""
    sql = """
        INSERT INTO Log (habit_id, success, note, log_time)
        VALUES (?, ?, ?, ?)
    """
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (habit_id, success, note, log_time))
            log_id = cursor.lastrowid  # Get the last inserted ID
            print(f"New log entry ID: {log_id}")  # Debug print
            return log_id
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        raise
    except Exception as e:
        print(f"Error adding log entry: {e}")
        raise


def get_logs_by_habit(habit_id):
    """Retrieve all logs for a specific habit."""
    with create_connection() as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM Log WHERE habit_id = ?
        """, (habit_id,))
        return cursor.fetchall()


def get_last_log_entry(habit_id):
    """Retrieve the last log entry for a specific habit with specific notes."""
    with create_connection() as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM Log 
        WHERE habit_id = ? AND (note = 'Habit completed successfully on time' OR note = 'Habit marked as incomplete')
        ORDER BY log_time DESC LIMIT 1
        """, (habit_id,))
        return cursor.fetchone()


def clear_user_table():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM User")
            conn.commit()
            print("User table cleared successfully.")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error: Unable to establish database connection.")


def clear_habit_table():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Habit")
            conn.commit()
            print("Habit table cleared successfully.")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error: Unable to establish database connection.")


def clear_log_table():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Log")
            conn.commit()
            print("Log table cleared successfully.")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error: Unable to establish database connection.")


def count_success(habit_id):
    """Count aggregate success for a specific habit."""
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM Log WHERE habit_id = ? AND success = 1
                """, (habit_id,))
        return cursor.fetchone()[0]


def count_failure(habit_id):
    """Count aggregate success for a specific habit."""
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM Log WHERE habit_id = ? AND success = 0
                """, (habit_id,))
        return cursor.fetchone()[0]


def count_success_by_habit(habit_id):
    """Count aggregate success for a specific habit."""
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM Log WHERE habit_id = ? AND note = 'Habit completed successfully on time'
                """, (habit_id,))
        return cursor.fetchone()[0]


def count_unsuccessful_by_habit(habit_id):
    """Count aggregate success for a specific habit."""
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM Log WHERE habit_id = ? AND note = 'Habit marked as incomplete'
                """, (habit_id,))
        return cursor.fetchone()[0]


def count_consecutive_incomplete(habit_id):
    """Count consecutive incomplete logs for a specific habit."""
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT habit_id, success, note, log_time,
                    CASE WHEN note = 'Habit marked as incomplete' THEN
                    LAG(note) OVER (ORDER BY log_time) END AS previous_note
                    FROM Log
                    WHERE habit_id = ?
                ) AS subquery
                WHERE note = 'Habit marked as incomplete' AND (previous_note IS NULL OR previous_note = 'Habit marked as incomplete')
                """, (habit_id,))
        return cursor.fetchone()[0]


if __name__ == '__main__':
    create_tables()
