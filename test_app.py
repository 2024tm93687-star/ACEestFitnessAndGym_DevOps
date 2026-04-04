import pytest
from app import app, service

@pytest.fixture
def client():
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
    assert 'Assault Bike' in data['workout']
    assert data['color'] == '#e74c3c'
    assert data['calorie_factor'] == 22


def test_program_detail_muscle_gain(client):
    response = client.get('/programs/muscle-gain-mg')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Muscle Gain (MG)'
    assert 'Squat 5x5' in data['workout']
    assert data['color'] == '#2ecc71'
    assert data['calorie_factor'] == 35


def test_program_detail_beginner(client):
    response = client.get('/programs/beginner-bg')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Beginner (BG)'
    assert 'Full Body Circuit' in data['workout']
    assert data['color'] == '#3498db'
    assert data['calorie_factor'] == 26


def test_invalid_program_returns_404(client):
    response = client.get('/programs/unknown')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Program not found'


def test_service_program_names():
    assert service.get_program_names() == ['Fat Loss (FL)', 'Muscle Gain (MG)', 'Beginner (BG)']
