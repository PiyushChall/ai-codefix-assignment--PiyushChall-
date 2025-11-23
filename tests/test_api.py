from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_local_fix_schema():
    payload = {
        "language": "python",
        "cwe": "CWE-89",
        "code": "user_input = input('name: ')\nquery = f\"SELECT * FROM users WHERE name = '{user_input}'\""
    }

    resp = client.post("/local_fix", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "fixed_code" in data
    assert "diff" in data
    assert "explanation" in data
    assert "model_used" in data
    assert "token_usage" in data
    assert "latency_ms" in data

    assert "input_tokens" in data["token_usage"]
    assert "output_tokens" in data["token_usage"]
