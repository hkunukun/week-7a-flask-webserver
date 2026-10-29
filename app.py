
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    ]

    if "email" in columns:
        conn.execute("ALTER TABLE students RENAME TO students_old")

        conn.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL
            )
        """)

        conn.execute("""
            INSERT INTO students (id, name, department)
            SELECT id, name, department
            FROM students_old
        """)

        conn.execute("DROP TABLE students_old")

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return "Welcome to Flask Web Server"

# Feature branch: Student Registration
# Student Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not department:
            return "Name and Department are required", 400

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO students (name, department) VALUES (?, ?)",
            (name, department)
        )

        conn.commit()
        conn.close()

        return f"""
        <h2>Student Registration Successful</h2>
        <p>Name: {name}</p>
        <p>Department: {department}</p>
        """

    return render_template("index.html")


# Student Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not department:
            return "Name and Department are required", 400

        conn = get_db_connection()

        student = conn.execute(
            "SELECT * FROM students WHERE name = ? AND department = ?",
            (name, department)
        ).fetchone()

        conn.close()

        if student:
            return f"""
            <h2>Student Login Successful</h2>
            <p>Welcome, {student['name']}!</p>
            <p>Department: {student['department']}</p>
            <a href="/students">View Student Information</a>
            """

        return "Invalid name or department. Please register first.", 401

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Login</title>
    </head>
    <body>
        <h2>Student Login</h2>

        <form method="POST">
            <label>Name:</label>
            <input type="text" name="name" required>
            <br><br>

            <label>Department:</label>
            <input type="text" name="department" required>
            <br><br>

            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """


# View All Students
@app.route("/students")
def students():
    conn = get_db_connection()

    student_list = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=student_list
    )


# Update Student Information
@app.route("/update/<int:student_id>", methods=["GET", "POST"])
def update_student(student_id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not department:
            conn.close()
            return "Name and Department are required", 400

        cursor = conn.execute(
            "UPDATE students SET name = ?, department = ? WHERE id = ?",
            (name, department, student_id)
        )

        conn.commit()
        updated = cursor.rowcount
        conn.close()

        if updated == 0:
            return "Student not found", 404

        return redirect(url_for("students"))

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template("update.html", student=student)


# Delete Student
@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return "Student not found", 404

    return redirect(url_for("students"))


@app.route("/invalid")
def invalid():
    return "Page not found", 404


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
