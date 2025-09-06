from django.db import models
from django.db import models
from django.conf import settings # Для ссылки на AUTH_USER_MODEL


class Moment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='moments')
    image = models.ImageField(upload_to='moments_photos/')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Момент пользователя {self.user.username} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"
