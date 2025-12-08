from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthCode(models.Model):
    code = models.CharField(max_length=6)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='code')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}-{self.code}"
