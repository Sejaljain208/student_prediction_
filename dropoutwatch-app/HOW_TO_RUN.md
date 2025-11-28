# How to Run DropoutWatch Application

## Prerequisites
- Python 3.8 or higher installed
- All dependencies installed (see Installation section)

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd d:\antigravity\minor_project\dropoutwatch-app
   ```

2. **Create a virtual environment (if not already created):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   .\venv\Scripts\activate
   ```

4. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Make sure you're in the project directory:**
   ```bash
   cd d:\antigravity\minor_project\dropoutwatch-app
   ```

2. **Activate the virtual environment (if not already activated):**
   ```bash
   .\venv\Scripts\activate
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Access the application:**
   - Open your web browser
   - Navigate to: **http://127.0.0.1:5001**
   - Or: **http://localhost:5001**

## Default Login Credentials

The application comes with demo accounts:

### Teacher Account
- **Username:** `teacher@school.edu`
- **Password:** `teacher123`

### Admin Account
- **Username:** `admin@school.edu`
- **Password:** `admin123`

## Troubleshooting

### Port Already in Use
If you see an error that port 5001 is already in use:
1. Stop any running instances of the application
2. Or change the port in `run.py` (line 15) to a different number like 5002

### Module Not Found Errors
If you see "ModuleNotFoundError":
1. Make sure your virtual environment is activated
2. Run: `pip install -r requirements.txt`

### Database Errors
If you see database-related errors:
1. Delete the `instance/dropout_watch.db` file
2. Restart the application - it will create a new database

## Stopping the Application

Press `Ctrl+C` in the terminal where the application is running.

## Features Available

Once logged in, you can:
- View the **Landing Page** with information about the system
- Access the **Teacher Dashboard** to see student risk assessments
- View individual **Student Details**
- Run **Batch Predictions** to update all student risk scores
- See **Risk Distribution Charts** and analytics

## Need Help?

If you encounter any issues:
1. Check that all dependencies are installed
2. Ensure Python 3.8+ is being used
3. Verify the virtual environment is activated
4. Check the terminal for error messages
