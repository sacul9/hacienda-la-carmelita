def test_health_check(client):
    """Verifica que el endpoint /health responde correctamente."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data


def test_root(client):
    """Verifica que el endpoint raíz responde."""
    response = client.get("/")
    assert response.status_code == 200
