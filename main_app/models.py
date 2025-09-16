from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=120, unique=True)
    short_code = models.CharField(max_length=10, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to="images/teams/", blank=True, null=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="teams_created"
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('team-detail', kwargs={'pk': self.id})


class Match(models.Model):
    STATUS = [
        ("SCHEDULED", "Scheduled"),
        ("LIVE", "Live"),
        ("FT", "Full Time"),
        ("POSTPONED", "Postponed"),
        ("CANCELLED", "Cancelled"),
    ]
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="away_matches")
    kickoff_at = models.DateTimeField()
    venue = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="SCHEDULED")
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="matches_created"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(home_team=models.F("away_team")), name="no_same_team"),
        ]
        unique_together = [("home_team", "away_team", "kickoff_at")]
        indexes = [
            models.Index(fields=["kickoff_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} @ {self.kickoff_at:%Y-%m-%d %H:%M}"
    
    def get_absolute_url(self):
        return reverse('match-detail', kwargs={'pk': self.pk})

    @property
    def outcome(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return "HOME"
        if self.home_score < self.away_score:
            return "AWAY"
        return "DRAW"


class Prediction(models.Model):
    PICK = [("HOME", "Home win"), ("DRAW", "Draw"), ("AWAY", "Away win")]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="predictions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # user-friendly fields (no stake, no model_key)
    pick = models.CharField(max_length=5, choices=PICK)

    # optional probabilities (0–1). If provided, should ~sum to 1.0
    p_home = models.FloatField(null=True, blank=True)
    p_draw = models.FloatField(null=True, blank=True)
    p_away = models.FloatField(null=True, blank=True)

    result_points = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "match")]     # one pick per user per match
        indexes = [models.Index(fields=["match", "user"])]

    def __str__(self):
        who = self.user.username if self.user else "Anonymous"
        return f"{who}: {self.pick} on {self.match}"

    def get_absolute_url(self):
        return reverse('prediction-detail', kwargs={'pk': self.pk})