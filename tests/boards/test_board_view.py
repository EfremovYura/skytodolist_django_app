import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import BoardParticipant


@pytest.mark.django_db()
class TestBoardRetrieveView:

    @pytest.fixture(autouse=True)
    def setup(self, board_participant):
        self.url = self.get_url(board_participant.board_id)

    @staticmethod
    def get_url(board_pk: int) -> str:
        return reverse("goals:board", kwargs={'pk': board_pk})

    def test_auth_required(self, client):
        """
        Неавторизованный пользователь не может просматривать доски
        """
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_retrieve_deleted_board(self, auth_client, board):
        """
        Пользователь не может просматривать удаленную доски
        """
        board.is_deleted = True
        board.save()

        response = auth_client.post(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


    def test_failed_to_retrieve_foreign_board(self, client, user_factory):
        """
        Пользователь не может просматривать чужую доски
        """
        another_user = user_factory.create()
        client.force_login(another_user)

        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db()
class TestBoardDestroyView:

    @pytest.fixture(autouse=True)
    def setup(self, board_participant):
        self.url = self.get_url(board_participant.board_id)

    @staticmethod
    def get_url(board_pk: int) -> str:
        return reverse("goals:board", kwargs={'pk': board_pk})

    def test_auth_required(self, client):
        """
        Неавторизованный пользователь не может просматривать доски
        """
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("role", [
        BoardParticipant.Role.writer,
        BoardParticipant.Role.reader,
    ], ids=["writer", "reader"])
    def test_not_owner_failed_to_delete_board(self, client, user_factory, board, board_participant_factory, role):
        """
        Не владелец не может удалить доску
        """
        another_user = user_factory.create()
        board_participant_factory.create(user=another_user, board=board, role=role)
        client.force_login(another_user)

        response = client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_have_to_delete_board(self, auth_client, board):
        """
        Владелец может удалить доску
        """
        response = auth_client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        board.refresh_from_db()
        assert board.is_deleted is True
