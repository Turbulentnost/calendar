from django.urls import path

from taskboard.views.admin_tasks import AdminTaskListCreateApi

urlpatterns = [
    path("tasks/", AdminTaskListCreateApi.as_view(), name="admin-tasks-list-create"),
]
