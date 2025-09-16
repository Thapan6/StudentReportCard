from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify
import sqlite3, csv, io, json, re

app = Flask(__name__)

# Student class with OOP and grading logic
class Student:
    def __init__(self, name, roll, marks):
        self.name = name
        self.roll = roll
        self.marks = marks
        self.total = sum(marks.values())
        self.percentage = self.total / len(marks)
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        if self.percentage >= 90:
            return 'A+'
        elif self.percentage >= 75:
            return 'A'
        elif self.percentage >= 60:
            return 'B'
        elif self.percentage >= 50:
            return 'C'
        else:
            return 'F'

# Initialize database
def init_db():
    with sqlite3.connect('students.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     roll TEXT,
                     marks TEXT,
                     total REAL,
                     percentage REAL,
                     grade TEXT)''')
        conn.commit()

init_db()

@app.route('/', methods=['GET'])
def index():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    search_query = request.args.get('search', '')
    if search_query:
        c.execute("SELECT * FROM students WHERE name LIKE ? OR roll LIKE ?", (f"%{search_query}%", f"%{search_query}%"))
    else:
        c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()

    processed_students = []
    top_student = None
    max_percentage = -1
    total_percentage = 0

    for s in students:
        try:
            marks = json.loads(s[3])
        except:
            marks = {'Math': 0, 'Science': 0, 'English': 0}

        percentage = round(s[5], 2)
        total_percentage += percentage

        student_obj = {
            'id': s[0],
            'name': s[1],
            'roll': s[2],
            'math': marks.get('Math', 0),
            'science': marks.get('Science', 0),
            'english': marks.get('English', 0),
            'total': s[4],
            'percentage': percentage,
            'grade': s[6]
        }

        if percentage > max_percentage:
            max_percentage = percentage
            top_student = s[1]

        processed_students.append(student_obj)

    total_students = len(processed_students)
    total_math = sum(s['math'] for s in processed_students)
    total_science = sum(s['science'] for s in processed_students)
    total_english = sum(s['english'] for s in processed_students)

    stats = {
        'total': total_students,
        'average_math': round(total_math / total_students, 2) if total_students else 0,
        'average_science': round(total_science / total_students, 2) if total_students else 0,
        'average_english': round(total_english / total_students, 2) if total_students else 0,
        'average_percentage': round(total_percentage / total_students, 2) if total_students else 0,
        'top_performer': top_student or 'N/A'
    }

    return render_template("index.html", students=processed_students, stats=stats)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    roll = request.form.get('roll')
    math = request.form.get('math')
    science = request.form.get('science')
    english = request.form.get('english')

    try:
        math, science, english = int(math), int(science), int(english)
        marks = {'Math': math, 'Science': science, 'English': english}
        student = Student(name, roll, marks)

        with sqlite3.connect('students.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO students (name, roll, marks, total, percentage, grade) VALUES (?, ?, ?, ?, ?, ?)",
                      (student.name, student.roll, json.dumps(marks), student.total, student.percentage, student.grade))
            conn.commit()
        return redirect('/')
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/get_student/<int:id>', methods=['GET'])
def get_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()

    if student:
        marks = json.loads(student[3])
        return jsonify({
            'id': student[0],
            'name': student[1],
            'roll': student[2],
            'math': marks.get('Math', 0),
            'science': marks.get('Science', 0),
            'english': marks.get('English', 0)
        })
    return jsonify({'error': 'Student not found'}), 404

@app.route('/edit/<int:id>', methods=['POST'])
def edit_student(id):
    name = request.form.get('name')
    roll = request.form.get('roll')
    math = request.form.get('math')
    science = request.form.get('science')
    english = request.form.get('english')

    try:
        math, science, english = int(math), int(science), int(english)
        marks = {'Math': math, 'Science': science, 'English': english}
        student = Student(name, roll, marks)

        with sqlite3.connect('students.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE students SET name=?, roll=?, marks=?, total=?, percentage=?, grade=? WHERE id=?",
                      (student.name, student.roll, json.dumps(marks), student.total, student.percentage, student.grade, id))
            conn.commit()
        return redirect('/')
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    try:
        with sqlite3.connect('students.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE id=?", (id,))
            conn.commit()
        return redirect('/')
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/download')
def download():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Roll', 'Math', 'Science', 'English', 'Total', 'Percentage', 'Grade'])

    for s in students:
        marks = json.loads(s[3])
        writer.writerow([
            s[0], s[1], s[2],
            marks.get('Math', 0), marks.get('Science', 0), marks.get('English', 0),
            s[4], round(s[5], 2), s[6]
        ])

    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), download_name="students.csv", as_attachment=True, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
