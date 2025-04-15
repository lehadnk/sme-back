def test_smth(test_client):
    response = test_client.get("/")
    assert response.status_code == 404