def test_get_subjects(client):
    resp = client.get('/api/subjects')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert isinstance(data['subjects'], list)


def test_get_categories(client):
    resp = client.get('/api/subjects/categories')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert isinstance(data['categories'], list)


def test_get_subject_not_found(client):
    resp = client.get('/api/subjects/9999')
    assert resp.status_code == 404


def test_preferences_crud(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Get (empty)
    resp = client.get('/api/preferences', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['preferences'] == []


def test_preferences_no_auth(client):
    resp = client.get('/api/preferences')
    assert resp.status_code == 401
