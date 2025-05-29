from fastapi import APIRouter

users_router = APIRouter()

@users_router.get("/users/list")
def get_users_list():
    print("In: get_users_list")

    return {
        "data": [
            {"id": 1, "username": "AlexeyZauzin", "role": "researcher"},
            {"id": 2, "username": "JuliaZauzina", "role": "researcher"},
            {"id": 3, "username": "PetrIvanov", "role": "researcher"},
            {"id": 4, "username": "JohnDoe", "role": "researcher"},
            {"id": 5, "username": "AlexHaffner", "role": "researcher"},
            {"id": 6, "username": "BurkhardWagner", "role": "researcher"},
        ],
        "count": 6
    }

@users_router.get("/users/{id}")
def get_user(id: int):
    print("In: get_user")

    return {
        "id": id,
        "username": "AlexeyZauzin",
        "role": "researcher",
    }