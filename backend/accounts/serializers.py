from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'email', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'company']

class RegisterCompanySerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_company_name(self, value):
        value = value.strip()
        if Company.objects.filter(company_name__iexact=value).exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if Company.objects.filter(email=value).exists():
            raise serializers.ValidationError("A company with this email already exists.")
        return value

    def create(self, validated_data):
        company_name = validated_data['company_name']
        email = validated_data['email']
        password = validated_data['password']

        company = Company.objects.create(company_name=company_name, email=email)

        user = User.objects.create_user(
            email=email,
            password=password,
            company=company
        )

        return user
