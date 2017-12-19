from django.db import models
from django.contrib.auth.hashers import make_password
# Create your models here.


class DashboardUsers(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(DashboardUsers, self).save(*args, **kwargs)
