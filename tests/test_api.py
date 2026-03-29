from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_user_journey() -> None:
    register = client.post('/users/register', json={'name': 'Arjun', 'email': 'arjun@example.com'})
    assert register.status_code == 200
    user = register.json()['user']

    # Persona creation should fail before verification
    pre = client.post(
        '/persona/upsert',
        json={
            'user_id': user['user_id'],
            'persona_name': 'Digital Arjun',
            'speaking_style': 'calm and direct',
            'beliefs': ['truth first'],
            'boundaries': ['financial advice'],
            'sample_phrases': ['Let me think clearly'],
        },
    )
    assert pre.status_code == 403

    verify = client.post(f"/users/{user['user_id']}/verify")
    assert verify.status_code == 200
    assert verify.json()['user']['is_verified'] is True

    persona = client.post(
        '/persona/upsert',
        json={
            'user_id': user['user_id'],
            'persona_name': 'Digital Arjun',
            'speaking_style': 'calm and direct',
            'beliefs': ['truth first'],
            'boundaries': ['financial advice'],
            'sample_phrases': ['Let me think clearly'],
        },
    )
    assert persona.status_code == 200

    safe_reply = client.post(
        '/chat',
        json={'user_id': user['user_id'], 'message': 'Give me financial advice now', 'mode': 'safe'},
    )
    assert safe_reply.status_code == 200
    assert 'boundary' in safe_reply.json()['reply'].lower()

    exact_reply = client.post(
        '/chat',
        json={'user_id': user['user_id'], 'message': 'How should I handle stress?', 'mode': 'exact'},
    )
    assert exact_reply.status_code == 200
    assert exact_reply.json()['persona_found'] is True
