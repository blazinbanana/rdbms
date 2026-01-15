# PyLiteDB & Employee Manager 🚀

A custom-built Relational Database Management System (RDBMS) from the ground up, featuring a SQL-like interface, persistent storage, and an integrated web dashboard.
🌟 The Challenge

Most web applications use pre-built databases like PostgreSQL or SQLite. This project implements the Database Engine itself, handling everything from query parsing to data indexing and persistence.
🛠️ Features
## 1. Custom RDBMS Engine (pylite_db.py)

    * SQL Parser: Uses Regex-based tokenization to support CREATE, INSERT, SELECT, JOIN, and DELETE.

    * Persistence: Tables are serialized to db_meta.json to ensure data survives server restarts.

    * Indexing: Implements a Hash Map Index (O(1) lookup) for Primary Keys.

    * Relational Joins: Supports INNER JOIN logic using a nested-loop join algorithm.

    * REPL: An interactive Command Line Interface for direct database interaction.

## 2. Web Application (app.py)

    Framework: Flask-based CRUD interface.

    Dynamic UI: Demonstrate relational data by joining "Employees" with "Departments" in real-time.

    Persistence Proof: Data remains intact across sessions.

##  Getting Started
### Prerequisites

    Python 3.x

    Flask (pip install flask)

### Running the Database REPL

To interact with the engine directly:
bash

python pylite_db.py

## ▶️ Running the Web App

    Install dependencies:
    bash

    pip install -r requirements.txt

    Start the server:
    bash

    python app.py

    Open in your browser:
    text

    http://localhost:5000

You can now run SQL-like queries directly from the web interface.
## 📂 Project Structure

.
├── app.py # Flask web server and API logic
├── pylite_db.py # Core database engine and SQL parser
├── db_meta.json # Persistent storage (auto-generated)
├── requirements.txt # Project dependencies
├── README.md
└── .gitignore

**Copyright 2026 Caleb Maina**