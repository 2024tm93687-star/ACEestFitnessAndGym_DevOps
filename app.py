import os

from flask import Flask, jsonify, abort

class ACEestService:
    def __init__(self):
        self.programs = {
            "Fat Loss (FL)": {
                "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
                "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
                "color": "#e74c3c",
                "slug": "fat-loss-fl"
            },
            "Muscle Gain (MG)": {
                "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
                "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
                "color": "#2ecc71",
                "slug": "muscle-gain-mg"
            },
            "Beginner (BG)": {
                "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
                "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day",
                "color": "#3498db",
                "slug": "beginner-bg"
            }
        }
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
                "color": data["color"]
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

service = ACEestService()
app = Flask(__name__)

@app.route('/')
def welcome():
    return jsonify({
        'message': 'Welcome to ACEest Fitness and Gym API',
        'routes': ['/programs', '/programs/<slug>']
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

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': error.description}), 404

if __name__ == '__main__':
    # Safe defaults for local execution; override via environment variables when needed.
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
