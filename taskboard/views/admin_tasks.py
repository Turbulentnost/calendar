from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.permissions import IsStaffWithAdminRole

from ..models import Task
from ..serializers import TaskSerializer


class AdminTaskListCreateApi(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsStaffWithAdminRole]

    def get_queryset(self):
        queryset = Task.objects.select_related("creator", "assignee").all()
        assignee = (self.request.query_params.get("assignee") or "").strip()
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
