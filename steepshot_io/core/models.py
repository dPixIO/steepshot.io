from django.db import models


class Subscribe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255, verbose_name=u'Your E-mail address')

    def __str__(self):
        return self.email


class TeamMembers(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    link_github = models.CharField(max_length=255, blank=True)
    link_linkedin = models.CharField(max_length=255,  blank=True)
    position = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='team/')

    def __str__(self):
        return self.last_name


class Vanancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


class Currency(models.Model):
    name = models.CharField(max_length=50)


class Investors(models.Model):
    email = models.EmailField()
    amount = models.FloatField()
    currency = models.ForeignKey(Currency)
    description = models.TextField()
