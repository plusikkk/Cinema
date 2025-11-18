
from django.urls import path
from registration.views import CreateUserView, ManageUserView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),
    path('manage/', ManageUserView.as_view(), name='manage'),
]