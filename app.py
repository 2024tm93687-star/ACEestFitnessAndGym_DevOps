import os
import io
import csv
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, abort, request, Response

class ACEestService:
    def __init__(self):
        self.db_name = os.getenv("ACEEST_DB_NAME", "aceest_fitness.db")
        self.programs = {
            "Fat Loss (FL)": {
                "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
                "diet": "Egg Whites, Chicken, Fish Curry",
                "color": "#e74c3c",
                "factor": 22,
                "slug": "fat-loss-fl"
            },
            "Muscle Gain (MG)": {
                "workout": "Squat, Bench, Deadlift, Press, Rows",
                "diet": "Eggs, Biryani, Mutton Curry",
                "color": "#2ecc71",
                "factor": 35,
                "slug": "muscle-gain-mg"
            },
            "Beginner (BG)": {
                "workout": "Air Squats, Ring Rows, Push-ups",
                "diet": "Balanced Tamil Meals",
                "color": "#3498db",
                "factor": 26,
                "slug": "beginner-bg"
            }
        }
        self.slug_map = {data['slug']: name for name, data in self.programs.items()}
        self.init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    age INTEGER,
                    weight REAL,
                    program TEXT,
                    calories INTEGER
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    week TEXT,
                    adherence INTEGER
                )
                """
            )
            conn.commit()

    def get_program_names(self):
        return list(self.programs.keys())

    def get_all_programs(self):
        return [
            {
                "name": name,
                "slug": data["slug"],
                "workout": data["workout"],
                "diet": data["diet"],
                "color": data["color"],
                "factor": data["factor"],
                # Backward-compatible alias for earlier API consumers.
                "calorie_factor": data["factor"]
            }
            for name, data in self.programs.items()
        ]

    def get_program_data(self, slug):
        program_name = self.slug_map.get(slug)
        if not program_name:
            return None
        program = self.programs[program_name].copy()
        # Backward-compatible alias for earlier API consumers.
        program["calorie_factor"] = program["factor"]
        program["name"] = program_name
        return program

    def add_client(self, payload):
        name = (payload.get("name") or "").strip()
        program = payload.get("program")

        if not name or not program:
            return None, "Please fill client name and program."

        if program not in self.programs:
            return None, "Invalid program selected."

        age = int(payload.get("age", 0) or 0)
        weight = float(payload.get("weight", 0) or 0)

        calories = int(weight * self.programs[program]["factor"])

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO clients (name, age, weight, program, calories)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, age, weight, program, calories),
            )
            conn.commit()

        client = {
            "name": name,
            "age": age,
            "weight": weight,
            "program": program,
            "calories": calories,
        }
        return client, None

    def get_clients(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, age, weight, program, calories FROM clients ORDER BY id")
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_client(self, name):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name, age, weight, program, calories FROM clients WHERE name=?",
                (name,),
            )
            row = cur.fetchone()
        return dict(row) if row else None

    def save_progress(self, payload):
        name = (payload.get("name") or "").strip()
        if not name:
            return None, "Name is required."

        adherence = int(payload.get("adherence", 0) or 0)
        week = payload.get("week") or datetime.now().strftime("Week %U - %Y")

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                (name, week, adherence),
            )
            conn.commit()

        return {"client_name": name, "week": week, "adherence": adherence}, None

    def get_progress(self, name):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT client_name, week, adherence FROM progress WHERE client_name=? ORDER BY id",
                (name,),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def reset_data(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM progress")
            cur.execute("DELETE FROM clients")
            conn.commit()

    def export_clients_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Age", "Weight", "Program", "Calories"])
        for client in self.get_clients():
            writer.writerow([
                client["name"],
                client["age"],
                client["weight"],
                client["program"],
                client["calories"],
            ])
        return output.getvalue()

service = ACEestService()
app = Flask(__name__)

@app.route('/')
def welcome():
    return jsonify({
        'message': 'Welcome to ACEest Fitness and Gym API',
        'routes': [
            '/programs',
            '/programs/<slug>',
            '/clients',
            '/clients/<name>',
            '/clients/export',
            '/progress',
            '/progress/<name>'
        ]
    })

@app.route('/programs')
def list_programs():
    return jsonify({
        'programs': service.get_program_names(),
        'count': len(service.get_program_names())
    })

@app.route('/programs/<slug>')
def program_detail(slug):
    program = service.get_program_data(slug)
    if program is None:
        abort(404, description='Program not found')
    return jsonify(program)


@app.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'GET':
        data = service.get_clients()
        return jsonify({'clients': data, 'count': len(data)})

    payload = request.get_json(silent=True) or {}
    client, error = service.add_client(payload)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': f"Client {client['name']} saved successfully.", 'client': client}), 201


@app.route('/clients/<name>')
def client_detail(name):
    client = service.get_client(name)
    if client is None:
        abort(404, description='Client not found')
    return jsonify(client)


@app.route('/clients/export')
def export_clients():
    csv_content = service.export_clients_csv()
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=clients.csv'}
    )


@app.route('/progress', methods=['POST'])
def progress():
    payload = request.get_json(silent=True) or {}
    record, error = service.save_progress(payload)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Weekly progress logged', 'progress': record}), 201


@app.route('/progress/<name>')
def progress_detail(name):
    data = service.get_progress(name)
    return jsonify({'progress': data, 'count': len(data)})

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': error.description}), 404

if __name__ == '__main__':
    # Safe defaults for local execution; override via environment variables when needed.
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
