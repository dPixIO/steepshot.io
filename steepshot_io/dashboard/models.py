from django.db import models
from django.contrib.auth.hashers import make_password
# Create your models here.


class DashboardUsers(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'user_dashboard'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(DashboardUsers, self).save(*args, **kwargs)
