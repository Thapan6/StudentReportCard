import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3, csv

# Initialize DB
conn = sqlite3.connect('students.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              roll TEXT,
              marks TEXT,
              total REAL,
              percentage REAL,
              grade TEXT)''')
conn.commit()

# Functions
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    c.execute("SELECT * FROM students")
    for row in c.fetchall():
        tree.insert('', 'end', values=row)

def add_student():
    try:
        name = name_var.get().strip()
        roll = roll_var.get().strip()
        math = math_var.get().strip()
        sci = science_var.get().strip()
        eng = english_var.get().strip()

        if not all([name, roll, math, sci, eng]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        math = int(math)
        sci = int(sci)
        eng = int(eng)

        if not (0 <= math <= 100 and 0 <= sci <= 100 and 0 <= eng <= 100):
            messagebox.showerror("Invalid Marks", "Marks must be between 0 and 100.")
            return

        marks = {'Math': math, 'Science': sci, 'English': eng}
        total = sum(marks.values())
        perc = round(total / 3, 2)

        if perc >= 90:
            grade = 'A+'
        elif perc >= 75:
            grade = 'A'
        elif perc >= 60:
            grade = 'B'
        elif perc >= 50:
            grade = 'C'
        else:
            grade = 'F'

        c.execute("INSERT INTO students (name, roll, marks, total, percentage, grade) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, roll, str(marks), total, perc, grade))
        conn.commit()
        refresh_table()
        clear_fields()
        messagebox.showinfo("Success", "Student added successfully!")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for marks.")
    except Exception as e:
        messagebox.showerror("Error", f"{e}")

def clear_fields():
    name_var.set("")
    roll_var.set("")
    math_var.set("")
    science_var.set("")
    english_var.set("")

def export_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Roll', 'Marks', 'Total', 'Percentage', 'Grade'])
            c.execute("SELECT * FROM students")
            writer.writerows(c.fetchall())
        messagebox.showinfo("Success", "Data exported successfully!")

# GUI Setup
root = tk.Tk()
root.title("Student Report Card System")
root.geometry("820x500")
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(pady=10)

name_var = tk.StringVar()
roll_var = tk.StringVar()
math_var = tk.StringVar()
science_var = tk.StringVar()
english_var = tk.StringVar()

tk.Label(frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(frame, textvariable=name_var, width=20).grid(row=0, column=1)

tk.Label(frame, text="Roll").grid(row=0, column=2, padx=5)
tk.Entry(frame, textvariable=roll_var, width=20).grid(row=0, column=3)

tk.Label(frame, text="Math").grid(row=1, column=0, padx=5)
tk.Entry(frame, textvariable=math_var, width=20).grid(row=1, column=1)

tk.Label(frame, text="Science").grid(row=1, column=2, padx=5)
tk.Entry(frame, textvariable=science_var, width=20).grid(row=1, column=3)

tk.Label(frame, text="English").grid(row=2, column=0, padx=5)
tk.Entry(frame, textvariable=english_var, width=20).grid(row=2, column=1)

tk.Button(frame, text="Add Student", command=add_student, bg="green", fg="white", width=15).grid(row=2, column=2, padx=10)
tk.Button(frame, text="Export CSV", command=export_csv, bg="blue", fg="white", width=15).grid(row=2, column=3, padx=10)

tree = ttk.Treeview(root, columns=("ID", "Name", "Roll", "Marks", "Total", "Percentage", "Grade"), show='headings')
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor='center')
tree.pack(pady=20, fill='x', padx=10)

refresh_table()
root.mainloop()
conn.close()
