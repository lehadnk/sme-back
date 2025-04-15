from faker import Faker

from persistence.postgres.db import save_user
from persistence.postgres.models import User

faker = Faker()

def create_test_researcher():
    researcher = User(
        role="researcher",
        username=faker.user_name(),
        password=faker.password()
    )
    save_user(researcher)

    return researcher