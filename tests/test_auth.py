def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'


def test_register(client):
    resp = client.post('/api/auth/register', json={
        'email': 'new@school.edu',
        'password': 'pass123',
        'first_name': 'New',
        'last_name': 'Student',
        'grade_level': 10
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    assert 'student_id' in data


def test_register_duplicate(client):
    payload = {
        'email': 'dup@school.edu',
        'password': 'pass123',
        'first_name': 'Dup',
        'last_name': 'Student',
        'grade_level': 10
    }
    client.post('/api/auth/register', json=payload)
    resp = client.post('/api/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_missing_fields(client):
    resp = client.post('/api/auth/register', json={'email': 'x@x.com'})
    assert resp.status_code == 400


def test_login_success(client):
    client.post('/api/auth/register', json={
        'email': 'login@school.edu',
        'password': 'pass123',
        'first_name': 'Login',
        'last_name': 'Test',
        'grade_level': 11
    })
    resp = client.post('/api/auth/login', json={
        'email': 'login@school.edu',
        'password': 'pass123'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'token' in data
    assert data['student']['email'] == 'login@school.edu'


def test_login_wrong_password(client):
    client.post('/api/auth/register', json={
        'email': 'wrong@school.edu',
        'password': 'pass123',
        'first_name': 'Wrong',
        'last_name': 'Pass',
        'grade_level': 9
    })
    resp = client.post('/api/auth/login', json={
        'email': 'wrong@school.edu',
        'password': 'wrongpass'
    })
    assert resp.status_code == 401


def test_logout(client):
    resp = client.post('/api/auth/logout')
    assert resp.status_code == 200
