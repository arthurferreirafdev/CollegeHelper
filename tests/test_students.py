def test_get_profile(client, auth_token):
    resp = client.get('/api/students/profile', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['student']['email'] == 'test@school.edu'


def test_get_profile_no_auth(client):
    resp = client.get('/api/students/profile')
    assert resp.status_code == 401


def test_update_profile(client, auth_token):
    resp = client.put('/api/students/profile', json={
        'first_name': 'Updated'
    }, headers={'Authorization': f'Bearer {auth_token}'})
    assert resp.status_code == 200

    resp = client.get('/api/students/profile', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    assert resp.get_json()['student']['first_name'] == 'Updated'
