from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import User
from user.serializers import UserReadSerializer


class UserSearchApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        users = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
        if query:
            users = users.filter(
                Q(nickname__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(department__icontains=query)
                | Q(job_title__icontains=query)
            )
        users = users.order_by("nickname")[:5]
        serializer = UserReadSerializer(users, many=True, context={"request": request})
        return Response({"results": serializer.data})
