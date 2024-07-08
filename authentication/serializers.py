from rest_framework import serializers
from .models import User, Organisation
from django.contrib.auth.hashers import make_password
import uuid

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'password', 'phone']
        extra_kwargs = {
            'password': {'write_only': True},
            'userId': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['userId'] = str(uuid.uuid4())
        return super(UserSerializer, self).create(validated_data)


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
        read_only_fields = ['orgId']
