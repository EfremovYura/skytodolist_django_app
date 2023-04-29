from django.urls import path

from goals import views


urlpatterns = [
    path("board/create", views.BoardCreateView.as_view(), name='board-create'),
    path("board/list", views.BoardListView.as_view(), name='board-list'),
    path("board/<int:pk>", views.BoardDetailView.as_view(), name='board'),

    path("goal_category/create", views.GoalCategoryCreateView.as_view(), name='category-create'),
    path("goal_category/list", views.GoalCategoryListView.as_view(), name='category-list'),
    path("goal_category/<int:pk>", views.GoalCategoryDetailView.as_view(), name='category'),

    path("goal/create", views.GoalCreateView.as_view(), name='goal-create'),
    path("goal/list", views.GoalListView.as_view(), name='goal-list'),
    path("goal/<int:pk>", views.GoalDetailView.as_view(), name='goal'),

    path('goal_comment/create', views.GoalCommentCreateView.as_view(), name='comment-create'),
    path('goal_comment/list', views.GoalCommentListView.as_view(), name='comment-list'),
    path('goal_comment/<int:pk>', views.GoalCommentDetailView.as_view(), name='comment'),
]
