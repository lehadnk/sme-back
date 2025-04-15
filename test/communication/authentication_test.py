from faker import Faker

from persistence.postgres.db import save_user
from persistence.postgres.models import User, UserRole

faker = Faker()

def test_authentication(test_client):
    username = faker.user_name()
    password = faker.password()

    user = User(
        username=username,
        role=UserRole.researcher,
        password=password
    )

    save_user(user)

    response = test_client.post("/authentication/login", json={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json().get("token")

    response = test_client.get("/authentication/current", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json().get("username") == username


