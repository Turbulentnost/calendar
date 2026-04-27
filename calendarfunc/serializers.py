from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.permissions import can_assign_to_user

from .models import Project, ProjectTask

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    creator_nickname = serializers.CharField(source="creator.nickname", read_only=True)
    password = serializers.CharField(write_only=True, min_length=1, required=False)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "login",
            "title",
            "creator",
            "creator_nickname",
            "room_created_at",
            "name",
            "image",
            "image_url",
            "description",
            "password",
        )
        read_only_fields = (
            "id",
            "creator",
            "creator_nickname",
            "room_created_at",
            "image_url",
        )

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Укажите название проекта.")
        return value

    def validate_name(self, value):
        return value.strip()

    def validate_login(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Укажите логин проекта.")
        qs = Project.objects.filter(login=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Проект с таким логином уже существует.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Укажите пароль проекта."})
        creator = self.context["request"].user
        project = Project.objects.create(creator=creator, **validated_data)
        project.set_password(password)
        project.save(update_fields=["password_hash"])
        return project

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save(update_fields=["password_hash"])
        return instance


class ProjectLoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_login(self, value):
        return value.strip()


class ProjectTaskSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source="author.nickname", read_only=True)
    assignee_nickname = serializers.CharField(source="assignee.nickname", read_only=True)

    class Meta:
        model = ProjectTask
        fields = (
            "id",
            "project",
            "author",
            "author_nickname",
            "assignee",
            "assignee_nickname",
            "date_from",
            "date_to",
            "short_description",
            "description",
            "deadline",
            "importance",
            "status",
            "is_closed",
            "is_carried_over",
            "carried_over_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "project",
            "author",
            "author_nickname",
            "assignee_nickname",
            "is_carried_over",
            "carried_over_at",
            "created_at",
            "updated_at",
        )

    def validate_short_description(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Укажите основное описание задачи.")
        if len(value.split()) > 20:
            raise serializers.ValidationError("Основное описание должно быть до 20 слов.")
        return value

    def validate(self, attrs):
        date_from = attrs.get("date_from", getattr(self.instance, "date_from", None))
        date_to = attrs.get("date_to", getattr(self.instance, "date_to", None))
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({"date_to": "Дата окончания не может быть раньше даты начала."})

        project = self.context["project"]
        actor = self.context["request"].user
        assignee = attrs.get("assignee", getattr(self.instance, "assignee", None))

        if assignee and not can_assign_to_user(actor, assignee):
            raise serializers.ValidationError(
                {"assignee": "Недостаточно прав для постановки задачи этому пользователю."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        task = super().update(instance, validated_data)
        if task.status == ProjectTask.STATUS_DONE and not task.is_closed:
            task.is_closed = True
            task.save(update_fields=["is_closed"])
        return task
