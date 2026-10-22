from flask import Flask, render_template, request

app = Flask(__name__)

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

        return f"Student Name: {name}<br>Department: {department}"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
