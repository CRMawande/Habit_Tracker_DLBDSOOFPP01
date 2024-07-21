--Create User Table
CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP);

--Create Habit Table
CREATE TABLE IF NOT EXISTS Habit (
            habit_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            periodicity TEXT NOT NULL,
            duration INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deadline TIMESTAMP,
            streak INTEGER DEFAULT 1,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES User (user_id)
        );

--Create Log Table
CREATE TABLE IF NOT EXISTS Log (
            log_id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 0,
            note TEXT,
            FOREIGN KEY (habit_id) REFERENCES Habit (habit_id));
