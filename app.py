#Copyright 2026 Caleb Maina
from flask import Flask, render_template_string, request, redirect, url_for
from pylite_db import Database

app = Flask(__name__)
db = Database()

#ensure tables exist on startup
db.execute("CREATE TABLE employees (id int, name str, dept str) PRIMARY KEY id")
db.execute("CREATE TABLE departments (name str, location str) PRIMARY KEY name")

#seed some data if empty
if not db.execute("SELECT * FROM departments"):
    db.execute("INSERT INTO departments VALUES ('Engineering', 'Building A')")
    db.execute("INSERT INTO departments VALUES ('HR', 'Building B')")

#HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PyLite Employee Manager</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .form-group { margin-bottom: 10px; }
        input, select { padding: 5px; }
        button { cursor: pointer; background: #007bff; color: white; border: none; padding: 5px 10px; }
        .delete-btn { background: #dc3545; }
    </style>
</head>
<body>
    <h1>PyLiteDB Manager</h1>
    
    <div style="background: #f9f9f9; padding: 15px; border-radius: 5px;">
        <h3>Add New Employee</h3>
        <form action="/add" method="POST">
            <input type="number" name="id" placeholder="ID (Unique)" required>
            <input type="text" name="name" placeholder="Name" required>
            <select name="dept">
                {% for dept in departments %}
                <option value="{{ dept.name }}">{{ dept.name }}</option>
                {% endfor %}
            </select>
            <button type="submit">Add Employee</button>
        </form>
    </div>

    <h3>Employee List (Joined with Departments)</h3>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Location (Joined)</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.dept }}</td>
                <td>{{ row.departments_location }}</td>
                <td>
                    <form action="/delete" method="POST" style="display:inline;">
                        <input type="hidden" name="id" value="{{ row.id }}">
                        <button type="submit" class="delete-btn">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    #demo for JOIN
    #joining employees with departments to show location
    query = "SELECT * FROM employees JOIN departments ON employees.dept=departments.name"
    rows = db.execute(query)
    
    #get departments for the dropdown
    depts = db.execute("SELECT * FROM departments")
    
    #handle case where database returns simple string on empty/error
    if isinstance(rows, str): rows = []
    if isinstance(depts, str): depts = []
    
    return render_template_string(HTML_TEMPLATE, rows=rows, departments=depts)

@app.route("/add", methods=["POST"])
def add_employee():
    try:
        id = request.form['id']
        name = request.form['name']
        dept = request.form['dept']
        db.execute(f"INSERT INTO employees VALUES ({id}, '{name}', '{dept}')")
    except Exception as e:
        print(f"Error adding: {e}")
    return redirect(url_for('index'))

@app.route("/delete", methods=["POST"])
def delete_employee():
    id = request.form['id']
    db.execute(f"DELETE FROM employees WHERE id={id}")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)