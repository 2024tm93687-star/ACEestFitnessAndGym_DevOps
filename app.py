import csv
import io
import os
import random
import sqlite3

_rng = random.SystemRandom()

from flask import Flask, Response, abort, jsonify, request


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
        self.slug_map = {p["slug"]: name for name, p in self.programs.items()}
        self._exercises_pool = {
            "Conditioning": [
                "Running", "Cycling", "Rowing", "Burpees", "Jump Rope", "Kettlebell Swings",
            ],
            "Hypertrophy": [
                "Leg Press", "Incline Dumbbell Press", "Lat Pulldown",
                "Lateral Raise", "Bicep Curl", "Tricep Extension",
            ],
            "Full Body": [
                "Push-Up", "Pull-Up", "Lunge", "Plank", "Dumbbell Row", "Dumbbell Press",
            ],
        }
        self._weekly_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
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
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )
                """
            )
            cur.execute(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'Admin')"
            )
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
                    target_adherence INTEGER,
                    membership_expiry TEXT
                )
                """
            )
            cur.execute("PRAGMA table_info(clients)")
            existing_cols = {row[1] for row in cur.fetchall()}
            if "membership_expiry" not in existing_cols:
                cur.execute("ALTER TABLE clients ADD COLUMN membership_expiry TEXT")
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

    def reset_data(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM exercises")
            cur.execute("DELETE FROM workouts")
            cur.execute("DELETE FROM metrics")
            cur.execute("DELETE FROM progress")
            cur.execute("DELETE FROM clients")
            cur.execute("DELETE FROM users")
            cur.execute(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'Admin')"
            )
            conn.commit()

    def login(self, username, password):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT username, role FROM users WHERE username=? AND password=?",
                (username, password),
            )
            row = cur.fetchone()
        return dict(row) if row else None

    def generate_ai_program(self, client_name, experience):
        valid_levels = ("beginner", "intermediate", "advanced")
        if experience not in valid_levels:
            return None, f"experience must be one of: {', '.join(valid_levels)}"

        client = self.get_client(client_name)
        if not client:
            return None, "Client not found"

        program_name = client.get("program", "")
        if "Fat Loss" in program_name:
            focus = "Conditioning"
        elif "Muscle Gain" in program_name:
            focus = "Hypertrophy"
        else:
            focus = "Full Body"

        if experience == "beginner":
            sets_range, reps_range, days = (2, 3), (8, 12), 3
        elif experience == "intermediate":
            sets_range, reps_range, days = (3, 4), (8, 15), 4
        else:
            sets_range, reps_range, days = (4, 5), (6, 15), 5

        pool = self._exercises_pool[focus]
        weekly_days = self._weekly_days[:days]
        ex_per_day = 3 if days < 4 else 4
        plan = []
        for day in weekly_days:
            for ex in _rng.sample(pool, k=min(ex_per_day, len(pool))):
                plan.append({
                    "day": day,
                    "exercise": ex,
                    "sets": _rng.randint(*sets_range),
                    "reps": _rng.randint(*reps_range),
                })
        return {"client_name": client_name, "experience": experience, "days": days, "plan": plan}, None

    def get_program_names(self):
        return list(self.programs.keys())

    def get_program_data(self, slug):
        name = self.slug_map.get(slug)
        if not name:
            return None
        data = self.programs[name].copy()
        data["name"] = name
        data["calorie_factor"] = data["factor"]
        return data

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
        membership_expiry = (payload.get("membership_expiry") or "").strip() or None
        calories = int(weight * self.programs[program]["factor"]) if weight else None

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO clients
                (name, age, height, weight, program, calories, target_weight, target_adherence, membership_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, age, height, weight, program, calories, target_weight, target_adherence, membership_expiry),
            )
            conn.commit()

        return self.get_client(name), None

    def get_clients(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT name, age, height, weight, program, calories,
                       target_weight, target_adherence, membership_expiry
                FROM clients ORDER BY name
                """
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_client(self, name):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT name, age, height, weight, program, calories,
                       target_weight, target_adherence, membership_expiry
                FROM clients WHERE name=?
                """,
                (name,),
            )
            row = cur.fetchone()
        return dict(row) if row else None

    def get_client_summary(self, name):
        client = self.get_client(name)
        if not client:
            return None

        progress = self.get_progress(name)
        metrics = self.get_metrics(name)
        avg_adherence = 0.0
        if progress:
            avg_adherence = round(sum(p["adherence"] for p in progress) / len(progress), 1)

        return {
            "client": client,
            "program_desc": self.programs.get(client["program"], {}).get("desc", ""),
            "progress_summary": {
                "weeks_logged": len(progress),
                "average_adherence": avg_adherence,
            },
            "last_metric": metrics[-1] if metrics else None,
        }

    def export_clients_csv(self):
        rows = self.get_clients()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Name", "Age", "Height", "Weight", "Program",
            "Calories", "TargetWeight", "TargetAdherence", "MembershipExpiry",
        ])
        for c in rows:
            writer.writerow([
                c.get("name"), c.get("age"), c.get("height"), c.get("weight"),
                c.get("program"), c.get("calories"), c.get("target_weight"),
                c.get("target_adherence"), c.get("membership_expiry"),
            ])
        return output.getvalue()

    def save_progress(self, payload):
        client_name = (payload.get("name") or "").strip()
        week = (payload.get("week") or "").strip()
        adherence = payload.get("adherence")
        if not client_name or adherence is None or not week:
            return None, "name, adherence, and week are required."

        adherence = int(adherence)
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                (client_name, week, adherence),
            )
            conn.commit()

        return {"client_name": client_name, "week": week, "adherence": adherence}, None

    def get_progress(self, name):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT client_name, week, adherence FROM progress WHERE client_name=? ORDER BY id",
                (name,),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_progress_chart(self, name):
        rows = self.get_progress(name)
        if not rows:
            return None
        return {
            "client_name": name,
            "weeks": [r["week"] for r in rows],
            "adherence": [r["adherence"] for r in rows],
        }

    def add_workout(self, payload):
        client_name = (payload.get("client_name") or "").strip()
        workout_date = (payload.get("date") or "").strip()
        workout_type = (payload.get("workout_type") or "").strip()
        if not client_name or not workout_date or not workout_type:
            return None, "client_name, date, and workout_type are required."

        duration_min = int(payload.get("duration_min") or 0)
        notes = (payload.get("notes") or "").strip()

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (client_name, workout_date, workout_type, duration_min, notes),
            )
            workout_id = cur.lastrowid

            for ex in payload.get("exercises", []):
                cur.execute(
                    """
                    INSERT INTO exercises (workout_id, name, sets, reps, weight)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        workout_id,
                        ex.get("name"),
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
                FROM metrics
                WHERE client_name=?
                ORDER BY date, id
                """,
                (client_name,),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_weight_chart(self, client_name):
        rows = [m for m in self.get_metrics(client_name) if m.get("weight") is not None]
        if not rows:
            return None
        return {
            "client_name": client_name,
            "dates": [r["date"] for r in rows],
            "weights": [r["weight"] for r in rows],
        }

    def get_bmi_info(self, client_name):
        client = self.get_client(client_name)
        if not client:
            return None, "Client not found"

        height_cm = float(client.get("height") or 0)
        weight = float(client.get("weight") or 0)
        if height_cm <= 0 or weight <= 0:
            return None, "Valid height and weight are required"

        height_m = height_cm / 100.0
        bmi = round(weight / (height_m * height_m), 1)
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


service = ACEestService()
app = Flask(__name__)


@app.route("/")
def welcome():
    return jsonify(
        {
            "message": "Welcome to ACEest Fitness and Gym API",
            "routes": [
                "/auth/login",
                "/programs",
                "/programs/<slug>",
                "/clients",
                "/clients/<name>",
                "/clients/<name>/summary",
                "/clients/<name>/bmi",
                "/clients/export",
                "/progress",
                "/progress/<name>",
                "/progress/<name>/chart",
                "/workouts",
                "/workouts/<name>",
                "/metrics",
                "/metrics/<name>",
                "/metrics/<name>/weight-chart",
                "/ai-program",
            ],
        }
    )


@app.route("/auth/login", methods=["POST"])
def auth_login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400
    user = service.login(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"message": "Login successful", "username": user["username"], "role": user["role"]})


@app.route("/programs")
def programs():
    names = service.get_program_names()
    return jsonify({"programs": names, "count": len(names)})


@app.route("/programs/<slug>")
def program_detail(slug):
    program = service.get_program_data(slug)
    if not program:
        abort(404, description="Program not found")
    return jsonify(program)


@app.route("/clients", methods=["GET", "POST"])
def clients():
    if request.method == "GET":
        rows = service.get_clients()
        return jsonify({"clients": rows, "count": len(rows)})

    payload = request.get_json(silent=True) or {}
    client, error = service.add_client(payload)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": f"Client {client['name']} saved successfully.", "client": client}), 201


@app.route("/clients/<name>")
def client_detail(name):
    client = service.get_client(name)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(client)


@app.route("/clients/<name>/summary")
def client_summary(name):
    summary = service.get_client_summary(name)
    if not summary:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(summary)


@app.route("/clients/<name>/bmi")
def client_bmi(name):
    bmi_info, error = service.get_bmi_info(name)
    if error:
        return jsonify({"error": error}), 404 if error == "Client not found" else 400
    return jsonify(bmi_info)


@app.route("/clients/export")
def export_clients():
    csv_data = service.export_clients_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients.csv"},
    )


@app.route("/progress", methods=["POST"])
def progress():
    payload = request.get_json(silent=True) or {}
    progress_data, error = service.save_progress(payload)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Weekly progress logged", "progress": progress_data}), 201


@app.route("/progress/<name>")
def progress_detail(name):
    data = service.get_progress(name)
    return jsonify({"progress": data, "count": len(data)})


@app.route("/progress/<name>/chart")
def progress_chart(name):
    data = service.get_progress_chart(name)
    if not data:
        return jsonify({"error": "No progress data available for this client"}), 404
    return jsonify(data)


@app.route("/workouts", methods=["POST"])
def workouts():
    payload = request.get_json(silent=True) or {}
    workout, error = service.add_workout(payload)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Workout logged successfully", "workout": workout}), 201


@app.route("/workouts/<name>")
def workout_history(name):
    rows = service.get_workouts(name)
    return jsonify({"workouts": rows, "count": len(rows)})


@app.route("/metrics", methods=["POST"])
def metrics():
    payload = request.get_json(silent=True) or {}
    metric, error = service.add_metrics(payload)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Metrics logged successfully", "metric": metric}), 201


@app.route("/metrics/<name>")
def metric_history(name):
    rows = service.get_metrics(name)
    return jsonify({"metrics": rows, "count": len(rows)})


@app.route("/metrics/<name>/weight-chart")
def weight_chart(name):
    data = service.get_weight_chart(name)
    if not data:
        return jsonify({"error": "No weight metrics available for this client"}), 404
    return jsonify(data)


@app.route("/ai-program", methods=["POST"])
def ai_program():
    payload = request.get_json(silent=True) or {}
    client_name = (payload.get("client_name") or "").strip()
    experience = (payload.get("experience") or "").strip().lower()
    if not client_name or not experience:
        return jsonify({"error": "client_name and experience are required"}), 400
    result, error = service.generate_ai_program(client_name, experience)
    if error:
        status = 404 if error == "Client not found" else 400
        return jsonify({"error": error}), status
    return jsonify(result), 201


@app.errorhandler(404)
def handle_not_found(error):
    description = getattr(error, "description", "Not found")
    return jsonify({"error": description}), 404


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
