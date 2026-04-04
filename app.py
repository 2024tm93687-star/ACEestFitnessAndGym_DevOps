import os
import io
import csv

from flask import Flask, jsonify, abort, request, Response

class ACEestService:
    def __init__(self):
        self.programs = {
            "Fat Loss (FL)": {
                "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
                "diet": "Egg Whites, Chicken, Fish Curry",
                "color": "#e74c3c",
                "calorie_factor": 22,
                "slug": "fat-loss-fl"
            },
            "Muscle Gain (MG)": {
                "workout": "Squat, Bench, Deadlift, Press, Rows",
                "diet": "Eggs, Biryani, Mutton Curry",
                "color": "#2ecc71",
                "calorie_factor": 35,
                "slug": "muscle-gain-mg"
            },
            "Beginner (BG)": {
                "workout": "Air Squats, Ring Rows, Push-ups",
                "diet": "Balanced Tamil Meals",
                "color": "#3498db",
                "calorie_factor": 26,
                "slug": "beginner-bg"
            }
        }
        self.clients = []
        self.slug_map = {data['slug']: name for name, data in self.programs.items()}

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
                "calorie_factor": data["calorie_factor"]
            }
            for name, data in self.programs.items()
        ]

    def get_program_data(self, slug):
        program_name = self.slug_map.get(slug)
        if not program_name:
            return None
        program = self.programs[program_name].copy()
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
        adherence = int(payload.get("adherence", 0) or 0)
        notes = (payload.get("notes") or "").strip()

        calorie_factor = self.programs[program]["calorie_factor"]
        estimated_calories = int(weight * calorie_factor) if weight > 0 else None

        client = {
            "name": name,
            "age": age,
            "weight": weight,
            "program": program,
            "adherence": adherence,
            "notes": notes,
            "estimated_calories": estimated_calories,
        }
        self.clients.append(client)
        return client, None

    def get_clients(self):
        return self.clients

    def export_clients_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
        for client in self.clients:
            writer.writerow(
                [
                    client["name"],
                    client["age"],
                    client["weight"],
                    client["program"],
                    client["adherence"],
                    client["notes"],
                ]
            )
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
            '/clients/export'
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


@app.route('/clients/export')
def export_clients():
    csv_content = service.export_clients_csv()
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=clients.csv'}
    )

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': error.description}), 404

if __name__ == '__main__':
    # Safe defaults for local execution; override via environment variables when needed.
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
