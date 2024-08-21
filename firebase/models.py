from django.db import models

# Create your models here.


class devicetoken(models.Model):

    userName = models.CharField(max_length=30, unique=True)
    fcm_token = models.CharField(max_length=400, null=False)
    log_status = models.BooleanField(default=False)
    team_request = models.TextField(default=[])
    player_request = models.TextField(default={})


class notificationMessage(models.Model):
    userName = models.CharField(max_length=30,)
    messages = models.CharField(blank=False, max_length=250)

