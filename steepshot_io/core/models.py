from django.db import models


class Subscribe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255, verbose_name=u'Your E-mail address')

    def __str__(self):
        return self.email
