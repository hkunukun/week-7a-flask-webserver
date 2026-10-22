
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    # Create the table if it does not exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)

    # Remove the old email requirement while preserving existing records
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        department = request.form.get("department")

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


@app.route("/update/<int:student_id>", methods=["GET", "POST"])
def update_student(student_id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name")
        department = request.form.get("department")

        if not name or not department:
            conn.close()
            return "Name and Department are required", 400

        cursor = conn.execute(
            "UPDATE students SET name=?, department=? WHERE id=?",
            (name, department, student_id)
        )

        conn.commit()
        updated = cursor.rowcount
        conn.close()

        if updated == 0:
            return "Student not found", 404

        return redirect(url_for("students"))

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template("update.html", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id=?",
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
