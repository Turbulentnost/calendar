from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from ..models import User
from ..permissions import IsStaffWithAdminRole
from ..serializers import UserCreateSerializer, UserReadSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("nickname")
    permission_classes = [IsStaffWithAdminRole]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserReadSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        out = UserReadSerializer(user, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)
