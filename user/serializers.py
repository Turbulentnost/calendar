from rest_framework import serializers

from .models import User


class UserReadSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "photo",
            "photo_url",
            "app_role",
            "department",
            "job_title",
            "is_staff",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=1)
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "nickname",
            "password",
            "first_name",
            "last_name",
            "app_role",
            "department",
            "job_title",
            "is_staff",
            "is_active",
            "photo",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        photo = validated_data.pop("photo", None)
        user = User(**validated_data)
        user.set_password(password)
        if photo is not None:
            user.photo = photo
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "photo",
            "department",
            "job_title",
        )


class AdminUserSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = (
            "id",
            "nickname",
            "password",
            "first_name",
            "last_name",
            "photo",
            "photo_url",
            "app_role",
            "department",
            "job_title",
            "is_staff",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "photo_url")

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None

    def validate_nickname(self, value):
        qs = User.objects.filter(nickname=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Никнейм уже занят.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Укажите пароль."})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
