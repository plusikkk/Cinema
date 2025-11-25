from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Auth.serializers import UserSerializer
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
   serializer_class = UserSerializer
   authentication_classes = (JWTAuthentication,)
   permission_classes = (IsAuthenticated,)

   def get_object(self):
       return self.request.user





