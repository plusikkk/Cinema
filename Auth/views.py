from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.tokens import RefreshToken

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            send_act_email(user, request)
            return Response({"message": "User created successfully. Check email to activate your account"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivationView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Email confirmed",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username,
                             }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)


class ManageUserView(generics.RetrieveUpdateAPIView):
   serializer_class = UserSerializer
   authentication_classes = (JWTAuthentication,)
   permission_classes = (IsAuthenticated,)

   def get_object(self):
       return self.request.user





