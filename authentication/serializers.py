from rest_framework import serializers
from .models import User, Organisation
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['userId', 'first_name', 'last_name', 'email', 'password', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        errors = {}
        if not data.get('first_name'):
            errors['first_name'] = 'First name is required'
        if not data.get('last_name'):
            errors['last_name'] = 'Last name is required'
        if not data.get('email'):
            errors['email'] = 'Email is required'
        if not data.get('password'):
            errors['password'] = 'Password is required'
        if User.objects.filter(email=data.get('email')).exists():
            errors['email'] = 'User with this email already exists'
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description', 'users']
        read_only_fields = ['users']
