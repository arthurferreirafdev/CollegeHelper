import pytest

def test_create_grade_horaria(client, auth_token):
    response = client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1', 'status': 'draft'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert 'grade_id' in data

def test_create_duplicate_grade_horaria(client, auth_token):
    client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    response = client.post(
        '/api/grade-horaria',
        json={'semester': '2024.2'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 409

def test_get_grade_horaria(client, auth_token):
    client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    response = client.get(
        '/api/grade-horaria',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'grade' in data
    assert data['grade']['semester'] == '2024.1'

def test_get_grade_horaria_not_found(client, auth_token):
    response = client.get(
        '/api/grade-horaria',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 404

def test_update_grade_horaria(client, auth_token):
    create_response = client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    grade_id = create_response.get_json()['grade_id']
    
    response = client.put(
        f'/api/grade-horaria/{grade_id}',
        json={'semester': '2024.2', 'status': 'active'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_delete_grade_horaria(client, auth_token):
    create_response = client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    grade_id = create_response.get_json()['grade_id']
    
    response = client.delete(
        f'/api/grade-horaria/{grade_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_add_subject_to_grade(client, auth_token):
    create_response = client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    grade_id = create_response.get_json()['grade_id']
    
    response = client.post(
        f'/api/grade-horaria/{grade_id}/subjects',
        json={'subject_id': 1},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True

def test_remove_subject_from_grade(client, auth_token):
    create_response = client.post(
        '/api/grade-horaria',
        json={'semester': '2024.1'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    grade_id = create_response.get_json()['grade_id']
    
    client.post(
        f'/api/grade-horaria/{grade_id}/subjects',
        json={'subject_id': 1},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    response = client.delete(
        f'/api/grade-horaria/{grade_id}/subjects/1',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_grade_horaria_without_auth(client):
    response = client.get('/api/grade-horaria')
    assert response.status_code == 401
