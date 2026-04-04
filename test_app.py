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
    assert data['programs'] == ['Fat Loss (FL)', 'Muscle Gain (MG)', 'Beginner (BG)']
    assert data['count'] == 3


def test_program_detail_fat_loss(client):
    response = client.get('/programs/fat-loss-fl')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Fat Loss (FL)'
    assert 'Back Squat' in data['workout']
    assert data['color'] == '#e74c3c'
    assert data['calorie_factor'] == 22


def test_program_detail_muscle_gain(client):
    response = client.get('/programs/muscle-gain-mg')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Muscle Gain (MG)'
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
    assert service.get_program_names() == ['Fat Loss (FL)', 'Muscle Gain (MG)', 'Beginner (BG)']


def test_create_client_success(client):
    response = client.post('/clients', json={
        'name': 'Asha',
        'age': 28,
        'weight': 60,
        'program': 'Fat Loss (FL)'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['client']['name'] == 'Asha'
    assert data['client']['calories'] == 1320


def test_create_client_validation_error(client):
    response = client.post('/clients', json={
        'name': '',
        'program': ''
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Please fill client name and program.'


def test_export_clients_csv(client):
    client.post('/clients', json={
        'name': 'Kumar',
        'age': 35,
        'weight': 72,
        'program': 'Muscle Gain (MG)'
    })
    response = client.get('/clients/export')
    assert response.status_code == 200
    assert 'text/csv' in response.content_type
    content = response.get_data(as_text=True)
    assert 'Name,Age,Weight,Program,Calories' in content
    assert 'Kumar' in content


def test_load_client_by_name(client):
    client.post('/clients', json={
        'name': 'Kavin',
        'age': 31,
        'weight': 70,
        'program': 'Beginner (BG)'
    })

    response = client.get('/clients/Kavin')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Kavin'
    assert data['program'] == 'Beginner (BG)'
    assert data['calories'] == 1820


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
