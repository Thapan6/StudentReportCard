import sqlite3
import json
import ast

# Connect to your database
conn = sqlite3.connect('students.db')
c = conn.cursor()

# Get all students
c.execute("SELECT id, marks FROM students")
students = c.fetchall()

# Fix each entry
for student_id, marks_str in students:
    try:
        # Try to load as JSON first
        marks = json.loads(marks_str)
    except json.JSONDecodeError:
        try:
            # If that fails, try to parse as Python literal
            marks = ast.literal_eval(marks_str)
            # Update with proper JSON
            c.execute("UPDATE students SET marks=? WHERE id=?", 
                      (json.dumps(marks), student_id))
        except:
            # If all fails, set default marks
            default_marks = {'Math': 0, 'Science': 0, 'English': 0}
            c.execute("UPDATE students SET marks=? WHERE id=?", 
                      (json.dumps(default_marks), student_id))

# Commit changes and close
conn.commit()
conn.close()