from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthCode
from .serializers import UserSerializer
from rest_framework import generics, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from Auth.utils import send_act_email

User = get_user_model()
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        existing_user = User.objects.filter(email__exact=email).first() or User.objects.filter(username__exact=username).first()

        if existing_user:
            if not existing_user.is_active:
                serializer = self.get_serializer(existing_user, data=request.data, partial=True)

                try:
                    serializer.is_valid(raise_exception=True)
                    existing_user = serializer.save()
                except Exception as e:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


                try:
                    send_act_email(existing_user, request)
                    return Response({"message": "New activation code sent", "email": existing_user.email}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response({"message": "Користувач з таким email вже існує", "email": email}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            send_act_email(user, request)
            return Response({"message": "User created successfully. Code sent to email", "email": user.email}, status=status.HTTP_201_CREATED)
        except Exception as e:
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email and Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            activation_record = AuthCode.objects.get(user=user)
        except (User.DoesNotExist, AuthCode.DoesNotExist):
            return Response({"error": "User or code not found"}, status=status.HTTP_404_NOT_FOUND)

        if activation_record.code != code:
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        if (timezone.now() - activation_record.created_at) > timedelta(minutes=3):
            return Response({"error": "Code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        activation_record.delete()
        refresh = RefreshToken.for_user(user)

        return Response({
                "message": "Email confirmed",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username,
                             }, status=status.HTTP_200_OK)

class ResendCodeView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"message": "Account has already active. Just log in."}, status=status.HTTP_400_BAD_REQUEST)
            send_act_email(user, request)
            return Response({"message": "New code sent"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ManageUserView(generics.RetrieveUpdateAPIView):
   serializer_class = UserSerializer
   authentication_classes = (JWTAuthentication,)
   permission_classes = (IsAuthenticated,)

   def get_object(self):
       return self.request.user





