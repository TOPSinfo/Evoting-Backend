from xml.parsers.expat import model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from account.models import CustomUser

PHASES = [
    (0, "REGISTER"),
    (1, "VOTING"),
    (2, "CLOSING"),
]


# Create your models here.
class Candidates(models.Model):
    full_name = models.CharField(_("Full Name"), max_length=255)
    party_name = models.CharField(_("Party Name"), max_length=255)

    qualification = models.CharField(
        _("Qualification"), max_length=255, default="", blank=True, null=True
    )
    age = models.IntegerField(_("Age"), default=0)
    is_active = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.full_name is not None:
            return self.full_name
        return "Unknown Candidate"

    def save(self, *args, **kwargs):
        if not self.id:
            self.is_active = True
        return super().save(*args, **kwargs)


class CandidatesVotes(models.Model):
    candidate = models.ForeignKey(
        Candidates, on_delete=models.CASCADE, related_name="candidate_votes"
    )
    votes = models.IntegerField(_("Votes"), default=0)
    users = models.ManyToManyField(CustomUser)
    is_active = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.candidate is not None:
            return self.candidate.full_name
        return "Unknown Candidate"

    def save(self, *args, **kwargs):
        if not self.id:
            self.is_active = True
        return super().save(*args, **kwargs)


class SystemPhases(models.Model):
    phase = models.IntegerField(
        _("System Phases"), default=PHASES[0][0], choices=PHASES
    )
