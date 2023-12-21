from django.urls import path
from .views import *

urlpatterns = [
    path("candidate/add/", CandidatesView.as_view(), name="candidate_add"),
    path(
        "candidate/list/", ListAndRetrieveCandidateView.as_view(), name="candidate_list"
    ),
    path(
        "candidate/view/<int:pk>",
        DetailAndRetrieveCandidateView.as_view(),
        name="candidate_detail_view",
    ),
    path(
        "candidate/approve/",
        ApproveSingleCandidateView.as_view(),
        name="candidate_approve",
    ),
    path(
        "candidate/approve/list/",
        ApproveCandidatesView.as_view(),
        name="candidate_list_approve",
    ),
    path(
        "candidate/users/list/",
        ApproveCandidatesView.as_view(),
        name="candidate_userslist_nonapprove",
    ),
    path(
        "candidate/vote/",
        VoteView.as_view(),
        name="do_vote",
    ),
    path(
        "candidate/result/",
        VoteView.as_view(),
        name="result",
    ),
    path(
        "candidate/phase/change/",
        ChagePhaseView.as_view(),
        name="result",
    ),
    path(
        "candidate/phase/view/",
        ChagePhaseView.as_view(),
        name="phase",
    ),
    path(
        "candidate/statestics/",
        StatasticsDataView.as_view(),
        name="statestics",
    ),
]
