from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from django.db.utils import IntegrityError
import uuid

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save(userId=str(uuid.uuid4()))
                org_name = f"{user.first_name}'s Organisation"
                org = Organisation.objects.create(org_id=str(uuid.uuid4()), name=org_name)
                org.users.add(user)
                org.save()

                refresh = RefreshToken.for_user(user)
                response_data = {
                    'status': 'success',
                    'message': 'Registration successful',
                    'data': {
                        'accessToken': str(refresh.access_token),
                        'user': UserSerializer(user).data
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'status': 'Bad request', 'message': 'Registration unsuccessful', 'statusCode': 400}, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors = [{'field': field, 'message': error[0]} for field, error in serializer.errors.items()]
            return Response({'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                response_data = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'accessToken': str(refresh.access_token),
                        'user': UserSerializer(user).data
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Bad request', 'message': 'Authentication failed', 'statusCode': 401}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'status': 'Bad request', 'message': 'Authentication failed', 'statusCode': 401}, status=status.HTTP_401_UNAUTHORIZED)
