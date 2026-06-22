from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterCompanySerializer, UserSerializer

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [] # Allow unauthenticated registration

    def post(self, request):
        serializer = RegisterCompanySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'company': {
                        'id': user.company.id,
                        'company_name': user.company.company_name,
                        'email': user.company.email
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [] # Allow unauthenticated login

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        # Standard authenticate checks USERNAME_FIELD which is 'email' in our custom model
        user = authenticate(email=email, password=password)
        if user is not None:
            if not user.is_active:
                return Response({'detail': 'User account is inactive.'}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'company': {
                        'id': user.company.id if user.company else None,
                        'company_name': user.company.company_name if user.company else None,
                        'email': user.company.email if user.company else None
                    }
                }
            }, status=status.HTTP_200_OK)
            
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
