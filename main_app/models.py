from django.db import models
# Create your models here.
GENDER = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]


class Players(models.Model):
    userName = models.CharField(max_length=70, primary_key=True, blank=False)
    name = models.CharField(max_length=100, null=True)
    pic = models.ImageField(upload_to='player_pic/', null=True)
    address = models.CharField(max_length=200, blank=False)
    dob = models.DateField(null=True,)
    gender = models.CharField(choices=GENDER, blank=True, max_length=7, default='')
    height = models.CharField(null=True, max_length=10)
    weight = models.CharField(null=True, max_length=5)
    teams = models.TextField(default=[])
    referee = models.TextField(default=[])
    totalMatch = models.CharField(default={"Level 1": 0, "Level 2": 0, "Level 3": 0, "Level 4": 0}, max_length=400)
    points = models.CharField(default={"3pm": 0, "2pm": 0, "F.T": 0, "F.T attempt": 0, "3 attempt": 0, "2 attempt": 0},
                              max_length=400)
    assist = models.IntegerField(default=0)
    block = models.IntegerField(default=0)
    steal = models.IntegerField(default=0)
    rebound = models.CharField(default={"Offensive": 0, "Defensive": 0, }, max_length=200)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.address = self.address.lower()
        return super(Players, self).save(*args, **kwargs)


LEVEL = [
    ('3X3', '3x3'),
    ('5X5', '5X5')
]


class Team(models.Model):
    team_id = models.CharField(max_length=70, primary_key=True, blank=False)
    team_name = models.CharField(max_length=70, blank=False)
    team_pic = models.ImageField(upload_to='team_img/', null=True, blank=True,)
    owner = models.CharField(max_length=70, blank=False)
    players = models.TextField(default=[])
    tournament = models.TextField(default={})
    category = models.CharField(max_length=3, choices=LEVEL, default=LEVEL[1], blank=False)
    address = models.CharField(max_length=200, blank=False)
    totalMatch = models.CharField(default={"Level 1": 0, "Level 2": 0, "Level 3": 0, "Level 4": 0}, max_length=400)
    points = models.CharField(default={"3pm": 0, "2pm": 0, "F.T": 0, "F.T attempt": 0, "3 attempt": 0, "2 attempt": 0},
                              max_length=400)
    assist = models.IntegerField(default=0)
    block = models.IntegerField(default=0)
    steal = models.IntegerField(default=0)
    rebound = models.CharField(default={"Offensive": 0, "Defensive": 0, }, max_length=200)

    def save(self, *args, **kwargs):
        self.address = self.address.lower()
        return super(Team, self).save(*args, **kwargs)


class Tournament(models.Model):
    tour_id = models.CharField(max_length=70, primary_key=True, blank=False)
    tour_name = models.CharField(max_length=200, blank=False)
    tour_owner = models.CharField(max_length=70, blank=False, default='')
    tour_category = models.CharField(max_length=3, choices=LEVEL, default=LEVEL[1], blank=False)
    tour_venue = models.CharField(max_length=200, blank=False)
    tour_date = models.DateField(blank=False)
    tour_referee = models.TextField(blank=True, default=[])
    tour_description = models.TextField(blank=True)
    tour_teams = models.TextField(default=[])
    tour_registration = models.BooleanField(default=True)
    tour_fixture = models.ImageField(upload_to='tour_fixtures/', null=True, blank=True,)
    is_challenge = models.BooleanField(default=False)


class Match(models.Model):
    match_id = models.CharField(max_length=70, primary_key=True, blank=False)
    tour_id = models.CharField(max_length=70, blank=False)
    match_between = models.TextField(default={}, blank=False)
    team_a_3 = models.IntegerField(default=0)
    team_a_3_attempt = models.IntegerField(default=0)
    team_a_2 = models.IntegerField(default=0)
    team_a_2_attempt = models.IntegerField(default=0)
    team_a_1 = models.IntegerField(default=0)
    team_a_1_attempt = models.IntegerField(default=0)
    team_a_steal = models.IntegerField(default=0)
    team_a_block = models.IntegerField(default=0)
    team_a_assist = models.IntegerField(default=0)
    team_a_offensive_rebound = models.IntegerField(default=0)
    team_a_defensive_rebound = models.IntegerField(default=0)
    team_a_player_stats = models.TextField(default={})
    team_b_3 = models.IntegerField(default=0)
    team_b_3_attempt = models.IntegerField(default=0)
    team_b_2 = models.IntegerField(default=0)
    team_b_2_attempt = models.IntegerField(default=0)
    team_b_1 = models.IntegerField(default=0)
    team_b_1_attempt = models.IntegerField(default=0)
    team_b_steal = models.IntegerField(default=0)
    team_b_block = models.IntegerField(default=0)
    team_b_assist = models.IntegerField(default=0)
    team_b_offensive_rebound = models.IntegerField(default=0)
    team_b_defensive_rebound = models.IntegerField(default=0)
    team_b_player_stats = models.TextField(default={})
    date = models.DateTimeField(null=True)
    status = models.CharField(max_length=10, default='upcoming')
    quarter = models.CharField(max_length=5, default='1')
    match_venue = models.CharField(max_length=200, blank=False, null=True)


class TeamRanking(models.Model):
    team_rank_id = models.CharField(max_length=100, primary_key=True, blank=False, default='')
    team_name = models.CharField(max_length=70, blank=False, default='')
    points = models.IntegerField(default=0)
    rebound = models.IntegerField(default=0)
    assist = models.IntegerField(default=0)
    block = models.IntegerField(default=0)
    steal = models.IntegerField(default=0)


class PlayerRanking(models.Model):
    player_rank_id = models.CharField(max_length=100, primary_key=True, blank=False, default='')
    player_name = models.CharField(max_length=100, blank=False, default='')
    points = models.IntegerField(default=0)
    rebound = models.IntegerField(default=0)
    assist = models.IntegerField(default=0)
    block = models.IntegerField(default=0)
    steal = models.IntegerField(default=0)


class Youtube(models.Model):
    video_id = models.CharField(max_length=100, blank=False)
    is_live = models.BooleanField(default=False)

