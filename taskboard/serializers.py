from rest_framework import serializers

from user.permissions import can_assign_to_user

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    creator_nickname = serializers.CharField(source="creator.nickname", read_only=True)
    assignee_nickname = serializers.CharField(source="assignee.nickname", read_only=True)
    assignee_department = serializers.CharField(source="assignee.department", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "priority",
            "deadline",
            "status",
            "creator",
            "creator_nickname",
            "assignee",
            "assignee_nickname",
            "assignee_department",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "creator",
            "creator_nickname",
            "assignee_nickname",
            "assignee_department",
            "created_at",
            "updated_at",
        )

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Укажите название задачи.")
        return value

    def validate_assignee(self, value):
        request = self.context.get("request")
        if request and not can_assign_to_user(request.user, value):
            raise serializers.ValidationError(
                "Недостаточно прав для постановки задачи этому пользователю."
            )
        return value

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)
