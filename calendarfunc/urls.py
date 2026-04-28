from django.urls import path

from .views import (
    ProjectCurrentApi,
    ProjectDetailApi,
    ProjectListCreateApi,
    ProjectLoginApi,
    ProjectTaskCarryOverApi,
    ProjectTaskCloseApi,
    ProjectTaskDetailApi,
    ProjectTaskListCreateApi,
    ProjectTaskReopenApi,
)

urlpatterns = [
    path("projects/", ProjectListCreateApi.as_view(), name="calendar-projects-list-create"),
    path("projects/login/", ProjectLoginApi.as_view(), name="calendar-projects-login"),
    path("projects/join/", ProjectLoginApi.as_view(), name="calendar-projects-join"),
    path("projects/current/", ProjectCurrentApi.as_view(), name="calendar-projects-current"),
    path("projects/<int:pk>/", ProjectDetailApi.as_view(), name="calendar-projects-detail"),
    path("tasks/", ProjectTaskListCreateApi.as_view(), name="calendar-projects-tasks-list-create"),
    path("tasks/<int:pk>/", ProjectTaskDetailApi.as_view(), name="calendar-projects-tasks-detail"),
    path("tasks/<int:pk>/close/", ProjectTaskCloseApi.as_view(), name="calendar-projects-tasks-close"),
    path("tasks/<int:pk>/reopen/", ProjectTaskReopenApi.as_view(), name="calendar-projects-tasks-reopen"),
    path("tasks/<int:pk>/carry-over/", ProjectTaskCarryOverApi.as_view(), name="calendar-projects-tasks-carry-over"),
]
