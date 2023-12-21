from django.contrib import admin
from .models import *


class CandidatesAdmin(admin.ModelAdmin):
    model = Candidates
    list_display = (
        "full_name",
        "party_name",
        "qualification",
        "date_created",
        "is_active",
    )
    list_filter = ("is_active",)


class CandidatesVotesAdmin(admin.ModelAdmin):
    model = CandidatesVotes
    list_display = (
        "candidate",
        "votes",
        "date_created",
        "is_active",
    )
    list_filter = ("is_active",)


# Register your models here.
admin.site.register(Candidates, CandidatesAdmin)
admin.site.register(CandidatesVotes, CandidatesVotesAdmin)
admin.site.register(SystemPhases)
