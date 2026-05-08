from django.urls import path

from .views import (
    AdminProjectListApi,
    ProjectCatalogListApi,
    ProjectCurrentApi,
    ProjectInviteApi,
    ProjectMemberDetailApi,
    ProjectMemberListApi,
    ProjectNotificationListApi,
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
    path("admin/projects/", AdminProjectListApi.as_view(), name="calendar-admin-projects"),
    path("projects/", ProjectListCreateApi.as_view(), name="calendar-projects-list-create"),
    path("projects/all/", ProjectCatalogListApi.as_view(), name="calendar-projects-all"),
    path("projects/login/", ProjectLoginApi.as_view(), name="calendar-projects-login"),
    path("projects/join/", ProjectLoginApi.as_view(), name="calendar-projects-join"),
    path("projects/current/", ProjectCurrentApi.as_view(), name="calendar-projects-current"),
    path("projects/current/invite/", ProjectInviteApi.as_view(), name="calendar-projects-invite"),
    path("projects/current/members/", ProjectMemberListApi.as_view(), name="calendar-projects-members"),
    path("notifications/", ProjectNotificationListApi.as_view(), name="calendar-notifications"),
    path(
        "projects/current/members/<int:user_id>/",
        ProjectMemberDetailApi.as_view(),
        name="calendar-projects-members-detail",
    ),
    path("projects/<int:pk>/", ProjectDetailApi.as_view(), name="calendar-projects-detail"),
    path("tasks/", ProjectTaskListCreateApi.as_view(), name="calendar-projects-tasks-list-create"),
    path("tasks/<int:pk>/", ProjectTaskDetailApi.as_view(), name="calendar-projects-tasks-detail"),
    path("tasks/<int:pk>/close/", ProjectTaskCloseApi.as_view(), name="calendar-projects-tasks-close"),
    path("tasks/<int:pk>/reopen/", ProjectTaskReopenApi.as_view(), name="calendar-projects-tasks-reopen"),
    path("tasks/<int:pk>/carry-over/", ProjectTaskCarryOverApi.as_view(), name="calendar-projects-tasks-carry-over"),
]
