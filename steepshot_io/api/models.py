from django.db import models
from django.template.loader import render_to_string

from steepshot_io.core.tasks import send_email
from steepshot_io.prod_settings import WORK_REQUEST_EMAILS


class Duration:
    w = 'w'
    m = 'm'
    mm = 'mm'
    y = 'y'
    o = 'o'
    not_sure = '?'


class Urgency:
    asap = '1'
    soon = '2'
    more = '3'


DURATION_CHOICES = (
    (Duration.w, 'A week or two'),
    (Duration.m, 'Around a month'),
    (Duration.mm, 'Several months'),
    (Duration.y, 'About a year'),
    (Duration.o, 'Long-term (ongoing)'),
    (Duration.not_sure, 'Not sure yet'),
)

URGENCY_CHOICES = (
    (Urgency.asap, 'ASAP (in one month or less)'),
    (Urgency.soon, 'Soon (in 1-3 months)'),
    (Urgency.more, 'In 3 months or more'),
)


class WorkRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    project_name = models.CharField(max_length=512)
    description = models.TextField()
    duration = models.CharField(max_length=7, choices=DURATION_CHOICES)
    urgency = models.CharField(max_length=7, choices=URGENCY_CHOICES)

    def save(self, *args, **kwargs):
        super(WorkRequest, self).save(*args, **kwargs)
        duration = dict(DURATION_CHOICES)
        ugrency = dict(URGENCY_CHOICES)
        context = {
            'name': self.name,
            'email': self.email,
            'project_name': self.project_name,
            'description': self.description,
            'duration': duration[self.duration],
            'urgency': ugrency[self.urgency],
        }
        content = render_to_string('email.html', context)
        send_email.delay(content, WORK_REQUEST_EMAILS)
