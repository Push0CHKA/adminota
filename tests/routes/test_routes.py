

def test_test_route(client):
    response = client.get("/test/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
