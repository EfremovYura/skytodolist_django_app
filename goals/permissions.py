from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from goals.models import BoardParticipant, Board


class BoardPermissions(IsAuthenticated):
    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Board) -> bool:
        _filters = {'user_id': request.user.id, 'board_id': obj.id}
        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCategoryPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        _filters = {'user_id': request.user.id, 'board_id': obj.board_id}
        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class GoalCommentPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
