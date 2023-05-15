from typing import Any
import pytest
from django.core.handlers.wsgi import WSGIRequest
from core.models import User

# --------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.fixture
def get_user_data() -> dict[str, str]:
    """This fixture serves to provide user data to create a new user's
    record
    :return: a dictionary containing user data
    """
    user_data = {
        "username": "test_username",
        "email": "testemail@test.com",
        "password": "test_password",
        "password_repeat": "test_password",
    }

    return user_data


@pytest.mark.django_db
@pytest.fixture
def updated_user_data(get_authorized_user) -> dict[str, Any]:
    """This fixture serves to provide user data to update user's profile
    :param get_authorized_user: a fixture returning a User model
    :return: a dictionary containing user data
    """
    user_data = {
        "id": get_authorized_user.id,
        "username": get_authorized_user.username,
        "first_name": "Ivan",
        "last_name": "Pupkin",
        "email": get_authorized_user.email,
    }

    return user_data


@pytest.mark.django_db
@pytest.fixture
def get_authorized_user(client, django_user_model) -> User:
    """This fixture serves to provide a registered user model
    :param django_user_model: a fixture providing access to User model
    :param client: a test client
    :return: User model
    """

    user_data = {
        "username": "test_username",
        "email": "testemail@test.com",
        "password": "test_password",
    }

    user = django_user_model.objects.create_user(**user_data)

    client.post("/core/login", data=user_data, content_type="application/json")

    return user


@pytest.mark.django_db
@pytest.fixture
def create_board(client, get_authorized_user) -> WSGIRequest:
    """This fixture serves to create a new board and return a response with
    the result of the operation
    :param get_authorized_user: a fixture providing registered user model
    :param client: a test client
    :return: WSGIResponse instance
    """
    board_data = {
        "title": "Test_Board",
    }

    response = client.post(
        "/goals/board/create", data=board_data, content_type="application/json"
    )

    return response


@pytest.mark.django_db
@pytest.fixture
def create_category(client, create_board) -> WSGIRequest:
    """This fixture serves to create a new category and return a response with
    the result of the operation
    :param create_board: a fixture providing response with created board's data
    :param client: a test client
    :return: WSGIResponse instance
    """
    category_data = {
        "title": "Test_Category",
        "board": create_board.data.get("id"),
    }

    response = client.post(
        "/goals/goal_category/create",
        data=category_data,
        content_type="application/json",
    )

    return response


@pytest.mark.django_db
@pytest.fixture
def create_goal(client, create_category) -> WSGIRequest:
    """This fixture serves to create a new goal and return a response with
    the result of the operation
    :param create_category: a fixture providing response with created
    category's data
    :param client: a test client
    :return: WSGIResponse instance
    """
    goal_data = {
        "title": "Test_Goal",
        "category": create_category.data.get("id"),
    }

    response = client.post(
        "/goals/goal/create", data=goal_data, content_type="application/json"
    )

    return response


@pytest.mark.django_db
@pytest.fixture
def create_comment(client, create_goal) -> WSGIRequest:
    """This fixture serves to create a new comment and return a response with
    the result of the operation
    :param create_goal: a fixture providing response with created
    goal's data
    :param client: a test client
    :return: WSGIResponse instance
    """
    comment_data = {
        "text": "Test_text",
        "goal": create_goal.data.get("id"),
    }

    response = client.post(
        "/goals/goal_comment/create", data=comment_data,
        content_type="application/json"
    )

    return response
