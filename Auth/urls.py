from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from Auth.views import CreateUserView, ManageUserView, ActivationView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),
    path('profile/', ManageUserView.as_view(), name='manage_user' ),
    path('verify/', ActivationView.as_view(), name='activate'),
]


