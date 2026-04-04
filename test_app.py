import pytest
from app import app, service

@pytest.fixture
def client():
    service.reset_data()
    return app.test_client()


def test_welcome_route(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Welcome to ACEest Fitness and Gym API'
    assert '/programs' in data['routes']


def test_list_programs(client):
    response = client.get('/programs')
    assert response.status_code == 200
    data = response.get_json()
    assert data['programs'] == ['Fat Loss (FL) - 3 day', 'Fat Loss (FL) - 5 day', 'Muscle Gain (MG) - PPL', 'Beginner (BG)']
    assert data['count'] == 4


def test_program_detail_fat_loss(client):
    response = client.get('/programs/fat-loss-fl-3-day')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Fat Loss (FL) - 3 day'
    assert 'Back Squat' in data['workout']
    assert data['color'] == '#e74c3c'
    assert data['calorie_factor'] == 22


def test_program_detail_muscle_gain(client):
    response = client.get('/programs/muscle-gain-mg-ppl')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Muscle Gain (MG) - PPL'
    assert 'Squat' in data['workout']
    assert data['color'] == '#2ecc71'
    assert data['calorie_factor'] == 35


def test_program_detail_beginner(client):
    response = client.get('/programs/beginner-bg')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Beginner (BG)'
    assert 'Air Squats' in data['workout']
    assert data['color'] == '#3498db'
    assert data['calorie_factor'] == 26


def test_invalid_program_returns_404(client):
    response = client.get('/programs/unknown')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Program not found'


def test_service_program_names():
    assert service.get_program_names() == ['Fat Loss (FL) - 3 day', 'Fat Loss (FL) - 5 day', 'Muscle Gain (MG) - PPL', 'Beginner (BG)']


def test_create_client_success(client):
    response = client.post('/clients', json={
        'name': 'Asha',
        'age': 28,
        'height': 165,
        'weight': 60,
        'program': 'Fat Loss (FL) - 3 day',
        'target_weight': 56,
        'target_adherence': 85
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['client']['name'] == 'Asha'
    assert data['client']['calories'] == 1320
    assert data['client']['height'] == 165.0


def test_create_client_validation_error(client):
    response = client.post('/clients', json={
        'name': '',
        'program': ''
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Name is required'


def test_export_clients_csv(client):
    client.post('/clients', json={
        'name': 'Kumar',
        'age': 35,
        'height': 175,
        'weight': 72,
        'program': 'Muscle Gain (MG) - PPL'
    })
    response = client.get('/clients/export')
    assert response.status_code == 200
    assert 'text/csv' in response.content_type
    content = response.get_data(as_text=True)
    assert 'Name,Age,Height,Weight,Program,Calories,TargetWeight,TargetAdherence,MembershipExpiry' in content
    assert 'Kumar' in content


def test_load_client_by_name(client):
    client.post('/clients', json={
        'name': 'Kavin',
        'age': 31,
        'height': 170,
        'weight': 70,
        'program': 'Beginner (BG)'
    })

    response = client.get('/clients/Kavin')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Kavin'
    assert data['program'] == 'Beginner (BG)'
    assert data['calories'] == 1820


def test_client_summary(client):
    client.post('/clients', json={
        'name': 'Arun',
        'age': 30,
        'height': 172,
        'weight': 78,
        'program': 'Fat Loss (FL) - 5 day'
    })
    client.post('/progress', json={'name': 'Arun', 'adherence': 80, 'week': 'Week 04 - 2026'})

    response = client.get('/clients/Arun/summary')
    assert response.status_code == 200
    data = response.get_json()
    assert data['client']['program'] == 'Fat Loss (FL) - 5 day'
    assert data['progress_summary']['weeks_logged'] == 1


def test_save_progress(client):
    response = client.post('/progress', json={
        'name': 'Asha',
        'adherence': 90,
        'week': 'Week 01 - 2026'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Weekly progress logged'
    assert data['progress']['adherence'] == 90


def test_get_progress_for_client(client):
    client.post('/progress', json={
        'name': 'Asha',
        'adherence': 75,
        'week': 'Week 02 - 2026'
    })

    response = client.get('/progress/Asha')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['progress'][0]['week'] == 'Week 02 - 2026'


def test_get_progress_chart_for_client(client):
    client.post('/progress', json={
        'name': 'Asha',
        'adherence': 80,
        'week': 'Week 03 - 2026'
    })

    response = client.get('/progress/Asha/chart')
    assert response.status_code == 200
    data = response.get_json()
    assert data['client_name'] == 'Asha'
    assert data['weeks'] == ['Week 03 - 2026']
    assert data['adherence'] == [80]


def test_get_progress_chart_no_data(client):
    response = client.get('/progress/Unknown/chart')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'No progress data available for this client'


def test_log_workout_and_get_history(client):
    response = client.post('/workouts', json={
        'client_name': 'Asha',
        'date': '2026-04-04',
        'workout_type': 'Strength',
        'duration_min': 60,
        'notes': 'Good session',
        'exercises': [
            {'name': 'Squat', 'sets': 3, 'reps': 5, 'weight': 80}
        ]
    })
    assert response.status_code == 201

    history = client.get('/workouts/Asha')
    assert history.status_code == 200
    data = history.get_json()
    assert data['count'] == 1
    assert data['workouts'][0]['workout_type'] == 'Strength'


def test_log_metrics_and_weight_chart(client):
    response = client.post('/metrics', json={
        'client_name': 'Asha',
        'date': '2026-04-04',
        'weight': 70,
        'waist': 84,
        'bodyfat': 18
    })
    assert response.status_code == 201

    chart = client.get('/metrics/Asha/weight-chart')
    assert chart.status_code == 200
    data = chart.get_json()
    assert data['dates'] == ['2026-04-04']
    assert data['weights'] == [70.0]


def test_bmi_endpoint(client):
    client.post('/clients', json={
        'name': 'Ravi',
        'age': 29,
        'height': 175,
        'weight': 75,
        'program': 'Beginner (BG)'
    })

    response = client.get('/clients/Ravi/bmi')
    assert response.status_code == 200
    data = response.get_json()
    assert data['client_name'] == 'Ravi'
    assert 'category' in data


def test_login_success(client):
    response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'admin'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'admin'
    assert data['role'] == 'Admin'


def test_login_failure(client):
    response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'wrong'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'Invalid credentials'


def test_ai_program_generation(client):
    client.post('/clients', json={
        'name': 'Priya',
        'age': 26,
        'height': 162,
        'weight': 58,
        'program': 'Fat Loss (FL) - 3 day'
    })

    response = client.post('/ai-program', json={
        'client_name': 'Priya',
        'experience': 'beginner'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['client_name'] == 'Priya'
    assert data['experience'] == 'beginner'
    assert data['days'] == 3
    assert isinstance(data['plan'], list)
    assert len(data['plan']) > 0
    first = data['plan'][0]
    assert 'day' in first
    assert 'exercise' in first
    assert 'sets' in first
    assert 'reps' in first


def test_ai_program_invalid_experience(client):
    client.post('/clients', json={
        'name': 'Priya',
        'age': 26,
        'height': 162,
        'weight': 58,
        'program': 'Fat Loss (FL) - 3 day'
    })

    response = client.post('/ai-program', json={
        'client_name': 'Priya',
        'experience': 'expert'
    })
    assert response.status_code == 400


def test_ai_program_client_not_found(client):
    response = client.post('/ai-program', json={
        'client_name': 'Unknown',
        'experience': 'beginner'
    })
    assert response.status_code == 404


def test_create_client_with_membership_expiry(client):
    response = client.post('/clients', json={
        'name': 'Meena',
        'age': 33,
        'height': 168,
        'weight': 65,
        'program': 'Beginner (BG)',
        'membership_expiry': '2026-12-31'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['client']['membership_expiry'] == '2026-12-31'
