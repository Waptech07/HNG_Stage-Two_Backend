from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models import User, Organisation
from authentication.serializers import UserSerializer, OrganisationSerializer
from django.shortcuts import get_object_or_404
import uuid

# Create your views here.

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        user = get_object_or_404(User, pk=id)
        
        if request.user == user or request.user.organisations.filter(pk__in=user.organisations.all()).exists():
            serializer = UserSerializer(user)
            return Response({
                "status": "success",
                "message": "User retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "Forbidden",
                "message": "You do not have permission to view this user",
            }, status=status.HTTP_403_FORBIDDEN)


class OrganisationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organisations = request.user.organisations.all()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {"organisations": serializer.data}
        }, status=status.HTTP_200_OK)
        
    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save(orgId=str(uuid.uuid4()))
            organisation.users.add(request.user)
            organisation.save()
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, orgId):
        organisation = get_object_or_404(Organisation, orgId=orgId)
        if request.user in organisation.users.all():
            serializer = OrganisationSerializer(organisation)
            return Response({
                "status": "success",
                "message": "Organisation retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "Forbidden",
                "message": "You do not have permission to view this organisation",
            }, status=status.HTTP_403_FORBIDDEN)

class AddUserToOrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, orgId):
        organisation = get_object_or_404(Organisation, orgId=orgId)
        if request.user not in organisation.users.all():
            return Response({
                "status": "Forbidden",
                "message": "You do not have permission to modify this organisation",
            }, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('userId')
        user = get_object_or_404(User, userId=user_id)
        if user in organisation.users.all():
            return Response({
                "status": "Bad Request",
                "message": "User already exists in this organisation",
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
                        
            organisation.users.add(user)
            organisation.save()
            return Response({
                "status": "success",
                "message": "User added to organisation successfully"
            }, status=status.HTTP_200_OK)
