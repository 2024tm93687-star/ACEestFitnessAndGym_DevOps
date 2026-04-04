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
            "Fat Loss (FL) - 3 day": {
                "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
                "diet": "Egg Whites, Chicken, Fish Curry",
                "color": "#e74c3c",
                "factor": 22,
                "desc": "3-day full-body fat loss",
                "slug": "fat-loss-fl-3-day",
            },
            "Fat Loss (FL) - 5 day": {
                "workout": "Higher-volume split with conditioning",
                "diet": "Lean protein, controlled carbs, hydration focus",
                "color": "#ff6b6b",
                "factor": 24,
                "desc": "5-day split, higher volume fat loss",
                "slug": "fat-loss-fl-5-day",
            },
            "Muscle Gain (MG) - PPL": {
                "workout": "Squat, Bench, Deadlift, Press, Rows",
                "diet": "Eggs, Biryani, Mutton Curry",
                "color": "#2ecc71",
                "factor": 35,
                "desc": "Push/Pull/Legs hypertrophy",
                "slug": "muscle-gain-mg-ppl",
            },
            "Beginner (BG)": {
                "workout": "Air Squats, Ring Rows, Push-ups",
                "diet": "Balanced Tamil Meals",
                "color": "#3498db",
                "factor": 26,
                "desc": "3-day simple beginner full-body",
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
                            "Fat Loss (FL) - 3 day": {
                                "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
                                "diet": "Egg Whites, Chicken, Fish Curry",
                                "color": "#e74c3c",
                                "factor": 22,
                                "desc": "3-day full-body fat loss",
                                "slug": "fat-loss-fl-3-day",
                            },
                            "Fat Loss (FL) - 5 day": {
                                "workout": "Higher-volume split with conditioning",
                                "diet": "Lean protein, controlled carbs, hydration focus",
                                "color": "#ff6b6b",
                                "factor": 24,
                                "desc": "5-day split, higher volume fat loss",
                                "slug": "fat-loss-fl-5-day",
                            },
                            "Muscle Gain (MG) - PPL": {
                                "workout": "Squat, Bench, Deadlift, Press, Rows",
                                "diet": "Eggs, Biryani, Mutton Curry",
                                "color": "#2ecc71",
                                "factor": 35,
                                "desc": "Push/Pull/Legs hypertrophy",
                                "slug": "muscle-gain-mg-ppl",
                            },
                            "Beginner (BG)": {
                                "workout": "Air Squats, Ring Rows, Push-ups",
                                "diet": "Balanced Tamil Meals",
                                "color": "#3498db",
                                "factor": 26,
                                "desc": "3-day simple beginner full-body",
                                "slug": "beginner-bg",
                            },
                        }
                        self.slug_map = {data["slug"]: name for name, data in self.programs.items()}
                        self.init_db()

                    def _connect(self):
                        conn = sqlite3.connect(self.db_name)
                        conn.row_factory = sqlite3.Row
                        return conn

                    def init_db(self):
                        with self._connect() as conn:
                            cur = conn.cursor()

                            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
                            exists = cur.fetchone() is not None
                            if exists:
                                cur.execute("PRAGMA table_info(clients)")
                                cols = {row[1] for row in cur.fetchall()}
                                required = {
                                    "id",
                                    "name",
                                    "age",
                                    "height",
                                    "weight",
                                    "program",
                                    "calories",
                                    "target_weight",
                                    "target_adherence",
                                }
                                if not required.issubset(cols):
                                    cur.execute("DROP TABLE clients")

                            cur.execute(
                                """
                                CREATE TABLE IF NOT EXISTS clients (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT UNIQUE,
                                    age INTEGER,
                                    height REAL,
                                    weight REAL,
                                    program TEXT,
                                    calories INTEGER,
                                    target_weight REAL,
                                    target_adherence INTEGER
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
                            cur.execute(
                                """
                                CREATE TABLE IF NOT EXISTS workouts (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    client_name TEXT,
                                    date TEXT,
                                    workout_type TEXT,
                                    duration_min INTEGER,
                                    notes TEXT
                                )
                                """
                            )
                            cur.execute(
                                """
                                CREATE TABLE IF NOT EXISTS exercises (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    workout_id INTEGER,
                                    name TEXT,
                                    sets INTEGER,
                                    reps INTEGER,
                                    weight REAL
                                )
                                """
                            )
                            cur.execute(
                                """
                                CREATE TABLE IF NOT EXISTS metrics (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    client_name TEXT,
                                    date TEXT,
                                    weight REAL,
                                    waist REAL,
                                    bodyfat REAL
                                )
                                """
                            )
                            conn.commit()

                    def get_program_names(self):
                        return list(self.programs.keys())

                    def get_program_data(self, slug):
                        program_name = self.slug_map.get(slug)
                        if not program_name:
                            return None
                        program = self.programs[program_name].copy()
                        program["calorie_factor"] = program["factor"]
                        program["name"] = program_name
                        return program

                    def add_client(self, payload):
                        name = (payload.get("name") or "").strip()
                        program = payload.get("program")
                        if not name:
                            return None, "Name is required"
                        if not program:
                            return None, "Program is required"
                        if program not in self.programs:
                            return None, "Invalid program selected."

                        age = int(payload.get("age") or 0) or None
                        height = float(payload.get("height") or 0) or None
                        weight = float(payload.get("weight") or 0) or None
                        target_weight = float(payload.get("target_weight") or 0) or None
                        target_adherence = int(payload.get("target_adherence") or 0) or None
                        calories = int(weight * self.programs[program]["factor"]) if weight else None

                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                """
                                INSERT OR REPLACE INTO clients
                                (name, age, height, weight, program, calories, target_weight, target_adherence)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (name, age, height, weight, program, calories, target_weight, target_adherence),
                            )
                            conn.commit()

                        return self.get_client(name), None

                    def get_clients(self):
                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                """
                                SELECT name, age, height, weight, program, calories, target_weight, target_adherence
                                FROM clients ORDER BY name
                                """
                            )
                            rows = cur.fetchall()
                        return [dict(r) for r in rows]

                    def get_client(self, name):
                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                """
                                SELECT name, age, height, weight, program, calories, target_weight, target_adherence
                                FROM clients WHERE name=?
                                """,
                                (name,),
                            )
                            row = cur.fetchone()
                        return dict(row) if row else None

                    def get_client_summary(self, name):
                        client = self.get_client(name)
                        if client is None:
                            return None

                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute("SELECT COUNT(*), AVG(adherence) FROM progress WHERE client_name=?", (name,))
                            total_weeks, avg_adherence = cur.fetchone()
                            avg_adherence = round(avg_adherence, 1) if avg_adherence is not None else 0

                            cur.execute(
                                "SELECT date, weight, waist, bodyfat FROM metrics WHERE client_name=? ORDER BY date DESC LIMIT 1",
                                (name,),
                            )
                            metric = cur.fetchone()

                        return {
                            "client": client,
                            "program_desc": self.programs.get(client["program"], {}).get("desc", ""),
                            "progress_summary": {
                                "weeks_logged": total_weeks,
                                "average_adherence": avg_adherence,
                            },
                            "last_metric": dict(metric) if metric else None,
                        }

                    def save_progress(self, payload):
                        name = (payload.get("name") or "").strip()
                        if not name:
                            return None, "Name is required."
                        adherence = int(payload.get("adherence") or 0)
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
                        return [dict(r) for r in rows]

                    def get_progress_chart(self, name):
                        records = self.get_progress(name)
                        if not records:
                            return None
                        return {
                            "client_name": name,
                            "weeks": [r["week"] for r in records],
                            "adherence": [r["adherence"] for r in records],
                        }

                    def add_workout(self, payload):
                        client_name = (payload.get("client_name") or "").strip()
                        workout_date = (payload.get("date") or "").strip()
                        workout_type = (payload.get("workout_type") or "").strip()
                        if not client_name or not workout_date or not workout_type:
                            return None, "client_name, date and workout_type are required."

                        duration_min = int(payload.get("duration_min") or 0)
                        notes = (payload.get("notes") or "").strip()
                        exercises = payload.get("exercises") or []

                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
                                (client_name, workout_date, workout_type, duration_min, notes),
                            )
                            workout_id = cur.lastrowid
                            for ex in exercises:
                                name = (ex.get("name") or "").strip()
                                if not name:
                                    continue
                                cur.execute(
                                    "INSERT INTO exercises (workout_id, name, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
                                    (workout_id, name, int(ex.get("sets") or 0), int(ex.get("reps") or 0), float(ex.get("weight") or 0)),
                                )
                            conn.commit()

                        return {
                            "id": workout_id,
                            "client_name": client_name,
                            "date": workout_date,
                            "workout_type": workout_type,
                            "duration_min": duration_min,
                            "notes": notes,
                        }, None

                    def get_workouts(self, name):
                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "SELECT id, date, workout_type, duration_min, notes FROM workouts WHERE client_name=? ORDER BY date DESC, id DESC",
                                (name,),
                            )
                            rows = cur.fetchall()
                        return [dict(r) for r in rows]

                    def add_metrics(self, payload):
                        client_name = (payload.get("client_name") or "").strip()
                        metric_date = (payload.get("date") or "").strip()
                        if not client_name or not metric_date:
                            return None, "client_name and date are required."
                        weight = float(payload.get("weight") or 0)
                        waist = float(payload.get("waist") or 0)
                        bodyfat = float(payload.get("bodyfat") or 0)

                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)",
                                (client_name, metric_date, weight, waist, bodyfat),
                            )
                            conn.commit()

                        return {
                            "client_name": client_name,
                            "date": metric_date,
                            "weight": weight,
                            "waist": waist,
                            "bodyfat": bodyfat,
                        }, None

                    def get_metrics(self, name):
                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "SELECT date, weight, waist, bodyfat FROM metrics WHERE client_name=? ORDER BY date",
                                (name,),
                            )
                            rows = cur.fetchall()
                        return [dict(r) for r in rows]

                    def get_weight_chart(self, name):
                        metrics = [m for m in self.get_metrics(name) if m.get("weight")]
                        if not metrics:
                            return None
                        return {
                            "client_name": name,
                            "dates": [m["date"] for m in metrics],
                            "weights": [m["weight"] for m in metrics],
                        }

                    def get_bmi_info(self, name):
                        client = self.get_client(name)
                        if not client:
                            return None, "Client not found"
                        height = float(client.get("height") or 0)
                        weight = float(client.get("weight") or 0)
                        if height <= 0 or weight <= 0:
                            return None, "Valid height and weight are required"

                        bmi = round(weight / ((height / 100.0) ** 2), 1)
                        if bmi < 18.5:
                            category = "Underweight"
                            risk = "Potential nutrient deficiency, low energy."
                        elif bmi < 25:
                            category = "Normal"
                            risk = "Low risk if active and strong."
                        elif bmi < 30:
                            category = "Overweight"
                            risk = "Moderate risk; focus on adherence and progressive activity."
                        else:
                            category = "Obese"
                            risk = "Higher risk; prioritize fat loss, consistency, and supervision."
                        return {"client_name": name, "bmi": bmi, "category": category, "risk": risk}, None

                    def reset_data(self):
                        with self._connect() as conn:
                            cur = conn.cursor()
                            cur.execute("DELETE FROM exercises")
                            cur.execute("DELETE FROM workouts")
                            cur.execute("DELETE FROM metrics")
                            cur.execute("DELETE FROM progress")
                            cur.execute("DELETE FROM clients")
                            conn.commit()

                    def export_clients_csv(self):
                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerow([
                            "Name",
                            "Age",
                            "Height",
                            "Weight",
                            "Program",
                            "Calories",
                            "TargetWeight",
                            "TargetAdherence",
                        ])
                        for c in self.get_clients():
                            writer.writerow([
                                c["name"],
                                c.get("age"),
                                c.get("height"),
                                c.get("weight"),
                                c.get("program"),
                                c.get("calories"),
                                c.get("target_weight"),
                                c.get("target_adherence"),
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
                            '/clients/<name>/summary',
                            '/clients/<name>/bmi',
                            '/clients/export',
                            '/progress',
                            '/progress/<name>',
                            '/progress/<name>/chart',
                            '/workouts',
                            '/workouts/<name>',
                            '/metrics',
                            '/metrics/<name>',
                            '/metrics/<name>/weight-chart',
                        ]
                    })


                @app.route('/programs')
                def list_programs():
                    return jsonify({'programs': service.get_program_names(), 'count': len(service.get_program_names())})


                @app.route('/programs/<slug>')
                def program_detail(slug):
                    data = service.get_program_data(slug)
                    if data is None:
                        abort(404, description='Program not found')
                    return jsonify(data)


                @app.route('/clients', methods=['GET', 'POST'])
                def clients():
                    if request.method == 'GET':
                        rows = service.get_clients()
                        return jsonify({'clients': rows, 'count': len(rows)})

                    payload = request.get_json(silent=True) or {}
                    row, error = service.add_client(payload)
                    if error:
                        return jsonify({'error': error}), 400
                    return jsonify({'message': f"Client {row['name']} saved successfully.", 'client': row}), 201


                @app.route('/clients/<name>')
                def client_detail(name):
                    row = service.get_client(name)
                    if row is None:
                        abort(404, description='Client not found')
                    return jsonify(row)


                @app.route('/clients/<name>/summary')
                def client_summary(name):
                    row = service.get_client_summary(name)
                    if row is None:
                        abort(404, description='Client not found')
                    return jsonify(row)


                @app.route('/clients/<name>/bmi')
                def client_bmi(name):
                    data, error = service.get_bmi_info(name)
                    if error:
                        if error == 'Client not found':
                            abort(404, description=error)
                        return jsonify({'error': error}), 400
                    return jsonify(data)


                @app.route('/clients/export')
                def export_clients():
                    csv_data = service.export_clients_csv()
                    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=clients.csv'})


                @app.route('/progress', methods=['POST'])
                def progress():
                    payload = request.get_json(silent=True) or {}
                    row, error = service.save_progress(payload)
                    if error:
                        return jsonify({'error': error}), 400
                    return jsonify({'message': 'Weekly progress logged', 'progress': row}), 201


                @app.route('/progress/<name>')
                def progress_detail(name):
                    rows = service.get_progress(name)
                    return jsonify({'progress': rows, 'count': len(rows)})


                @app.route('/progress/<name>/chart')
                def progress_chart(name):
                    data = service.get_progress_chart(name)
                    if data is None:
                        return jsonify({'error': 'No progress data available for this client'}), 404
                    return jsonify(data)


                @app.route('/workouts', methods=['POST'])
                def workouts():
                    payload = request.get_json(silent=True) or {}
                    row, error = service.add_workout(payload)
                    if error:
                        return jsonify({'error': error}), 400
                    return jsonify({'message': 'Workout logged successfully', 'workout': row}), 201


                @app.route('/workouts/<name>')
                def workout_history(name):
                    rows = service.get_workouts(name)
                    return jsonify({'workouts': rows, 'count': len(rows)})


                @app.route('/metrics', methods=['POST'])
                def metrics():
                    payload = request.get_json(silent=True) or {}
                    row, error = service.add_metrics(payload)
                    if error:
                        return jsonify({'error': error}), 400
                    return jsonify({'message': 'Metrics logged successfully', 'metric': row}), 201


                @app.route('/metrics/<name>')
                def metric_history(name):
                    rows = service.get_metrics(name)
                    return jsonify({'metrics': rows, 'count': len(rows)})


                @app.route('/metrics/<name>/weight-chart')
                def weight_chart(name):
                    data = service.get_weight_chart(name)
                    if data is None:
                        return jsonify({'error': 'No weight metrics available for this client'}), 404
                    return jsonify(data)


                @app.errorhandler(404)
                def handle_not_found(error):
                    return jsonify({'error': error.description}), 404


                if __name__ == '__main__':
                    host = os.getenv('FLASK_HOST', '127.0.0.1')
                    port = int(os.getenv('FLASK_PORT', '5000'))
                    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
                    app.run(host=host, port=port, debug=debug)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        workout_id,
                        name,
                        int(ex.get("sets") or 0),
                        int(ex.get("reps") or 0),
                        float(ex.get("weight") or 0),
                    ),
                )
            conn.commit()

        return {
            "id": workout_id,
            "client_name": client_name,
            "date": workout_date,
            "workout_type": workout_type,
            "duration_min": duration_min,
            "notes": notes,
        }, None

    def get_workouts(self, client_name):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, date, workout_type, duration_min, notes
                FROM workouts
                WHERE client_name=?
                ORDER BY date DESC, id DESC
                """,
                (client_name,),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def add_metrics(self, payload):
        client_name = (payload.get("client_name") or "").strip()
        metric_date = (payload.get("date") or "").strip()
        if not client_name or not metric_date:
            return None, "client_name and date are required."

        weight = float(payload.get("weight") or 0)
        waist = float(payload.get("waist") or 0)
        bodyfat = float(payload.get("bodyfat") or 0)

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
                VALUES (?, ?, ?, ?, ?)
                """,
                (client_name, metric_date, weight, waist, bodyfat),
            )
            conn.commit()

        return {
            "client_name": client_name,
            "date": metric_date,
            "weight": weight,
            "waist": waist,
            "bodyfat": bodyfat,
        }, None

    def get_metrics(self, client_name):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT date, weight, waist, bodyfat
                FROM metrics WHERE client_name=? ORDER BY date
                """,
                (client_name,),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_weight_chart(self, client_name):
        records = [m for m in self.get_metrics(client_name) if m.get("weight")]
        if not records:
            return None
        return {
            "client_name": client_name,
            "dates": [r["date"] for r in records],
            "weights": [r["weight"] for r in records],
        }

    def get_bmi_info(self, client_name):
        client = self.get_client(client_name)
        if not client:
            return None, "Client not found"

        height = float(client.get("height") or 0)
        weight = float(client.get("weight") or 0)
        if height <= 0 or weight <= 0:
            return None, "Valid height and weight are required"

        h_m = height / 100.0
        bmi = round(weight / (h_m * h_m), 1)
        if bmi < 18.5:
            category = "Underweight"
            risk = "Potential nutrient deficiency, low energy."
        elif bmi < 25:
            category = "Normal"
            risk = "Low risk if active and strong."
        elif bmi < 30:
            category = "Overweight"
            risk = "Moderate risk; focus on adherence and progressive activity."
        else:
            category = "Obese"
            risk = "Higher risk; prioritize fat loss, consistency, and supervision."

        return {
            "client_name": client_name,
            "bmi": bmi,
            "category": category,
            "risk": risk,
        }, None

    def reset_data(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM exercises")
            cur.execute("DELETE FROM workouts")
            cur.execute("DELETE FROM metrics")
            cur.execute("DELETE FROM progress")
            cur.execute("DELETE FROM clients")
            conn.commit()

    def export_clients_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Name",
            "Age",
            "Height",
            "Weight",
            "Program",
            "Calories",
            "TargetWeight",
            "TargetAdherence",
        ])
        for client in self.get_clients():
            writer.writerow([
                client["name"],
                client["age"],
                client.get("height"),
                client["weight"],
                client["program"],
                client["calories"],
                client.get("target_weight"),
                client.get("target_adherence"),
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
            '/clients/<name>/summary',
            '/clients/<name>/bmi',
            '/clients/export',
            '/progress',
            '/progress/<name>',
            '/progress/<name>/chart',
            '/workouts',
            '/workouts/<name>',
            '/metrics',
            '/metrics/<name>',
            '/metrics/<name>/weight-chart'
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


@app.route('/clients/<name>/summary')
def client_summary(name):
    summary = service.get_client_summary(name)
    if summary is None:
        abort(404, description='Client not found')
    return jsonify(summary)


@app.route('/clients/<name>/bmi')
def client_bmi(name):
    data, error = service.get_bmi_info(name)
    if error:
        if error == 'Client not found':
            abort(404, description=error)
        return jsonify({'error': error}), 400
    return jsonify(data)


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


@app.route('/progress/<name>/chart')
def progress_chart(name):
    data = service.get_progress_chart(name)
    if data is None:
        return jsonify({'error': 'No progress data available for this client'}), 404
    return jsonify(data)


@app.route('/workouts', methods=['POST'])
def workouts():
    payload = request.get_json(silent=True) or {}
    workout, error = service.add_workout(payload)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Workout logged successfully', 'workout': workout}), 201


@app.route('/workouts/<name>')
def workout_history(name):
    rows = service.get_workouts(name)
    return jsonify({'workouts': rows, 'count': len(rows)})


@app.route('/metrics', methods=['POST'])
def metrics():
    payload = request.get_json(silent=True) or {}
    metric, error = service.add_metrics(payload)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Metrics logged successfully', 'metric': metric}), 201


@app.route('/metrics/<name>')
def metric_history(name):
    rows = service.get_metrics(name)
    return jsonify({'metrics': rows, 'count': len(rows)})


@app.route('/metrics/<name>/weight-chart')
def weight_chart(name):
    data = service.get_weight_chart(name)
    if data is None:
        return jsonify({'error': 'No weight metrics available for this client'}), 404
    return jsonify(data)

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': error.description}), 404

if __name__ == '__main__':
    # Safe defaults for local execution; override via environment variables when needed.
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
