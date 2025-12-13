from django.urls import path
from Auth.views import CreateUserView, ManageUserView, ActivationView, ResendCodeView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),
    path('profile/', ManageUserView.as_view(), name='manage_user' ),
    path('verify/', ActivationView.as_view(), name='activate'),
    path('resend/', ResendCodeView.as_view(), name='resend'),
]


