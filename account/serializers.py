from rest_framework import serializers
from .models import CustomUser, UserProfile


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "full_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def validate_password(self, attrs):
        if len(attrs) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters!")

        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ("full_name", "email", "status", "is_active", "is_approved")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("address", "voter_id", "aadhar_no", "age")

    def validate_voter_id(self, attrs):
        if UserProfile.objects.filter(voter_id=attrs).exists():
            raise serializers.ValidationError("Voter ID is exists!")
        return super().validate(attrs)

    def validate_aadhar_no(self, attrs):
        if UserProfile.objects.filter(aadhar_no=attrs).exists():
            raise serializers.ValidationError("Aadhar No is exists!")
        return super().validate(attrs)

    def validate_age(self, attrs):
        if attrs < 18:
            raise serializers.ValidationError("Your age must be above 18 year!")
        return super().validate(attrs)
