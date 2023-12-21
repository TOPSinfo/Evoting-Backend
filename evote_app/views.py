from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
import logging


from account.models import USER_STATUS, UserProfile
from account.serializers import UserProfileSerializer, UserSerializer
from .serializers import *
from .models import *
from django.db import transaction
import datetime

# Create your views here.


class CandidatesView(generics.CreateAPIView):
    queryset = Candidates.objects.all()
    serializer_class = CandidateSserializer

    def post(self, request):
        # logging.info('request at'+str(datetime.datetime.now())+' hours!'+str(request))
        # logging.info('request.headers at'+str(datetime.datetime.now())+' hours!'+str(request.headers))
        # logging.info('request.data at'+str(datetime.datetime.now())+' hours!'+str(request.data))
        # logging.info('request.data.get("full_name") at'+str(datetime.datetime.now())+' hours!'+str(request.data.get("full_name")))
        cname = request.data.get("full_name")
        party_name = request.data.get("party_name")
        qualification = request.data.get("qualification")
        age = request.data.get("age")
        scr = Candidates.objects.create(
            full_name=cname, party_name=party_name, qualification=qualification, age=age
        )
        scr.save()
        return Response({"msg": "added"}, status=status.HTTP_201_CREATED)


class ListAndRetrieveCandidateView(generics.ListAPIView):
    queryset = Candidates.objects.all()
    serializer_class = CandidateSserializer


class DetailAndRetrieveCandidateView(generics.RetrieveAPIView):
    queryset = Candidates.objects.all()
    serializer_class = CandidateSserializer
    lookup_field = "pk"


class ApproveSingleCandidateView(APIView):
    def put(self, request):
        payload = {}

        address = request.data.get("address")

        if address is not None:
            profile = UserProfile.get_profile_by_address(address)
            if profile is not None:
                user = CustomUser.get_user(profile.user.id)
                if user.status == USER_STATUS[1][0]:
                    user.is_approved = True
                    user.save()
                    userSerializer = UserSerializer(user)
                    profileSerializer = UserProfileSerializer(profile)
                    payload = {
                        "user": userSerializer.data,
                        "profile": profileSerializer.data,
                        "message": "Voter is successfully Approved!",
                    }
                    return Response(payload, status=status.HTTP_204_NO_CONTENT)
                else:
                    payload = {"message": "You are not Registred as a Voter!"}
                    return Response(payload, status=status.HTTP_400_BAD_REQUEST)
            else:
                payload = {"message": "Invalid Address, Please Enter correct address!"}
                return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        else:
            payload = {"message": "Please provide a valid metamask account address!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


class ApproveCandidatesView(APIView):
    def get(self, request):
        payload = {}
        userlst = []
        non_approved_users = CustomUser.objects.filter(
            is_approved=False, is_superuser=False
        )
        if non_approved_users is not None:
            for user in non_approved_users:
                payload = {
                    "full_name": user.full_name,
                    "voter_id": user.user_profile.voter_id,
                    "aadhar_no": user.user_profile.aadhar_no,
                    "address": user.user_profile.address,
                    "is_approved": user.is_approved,
                }
                userlst.append(payload)
            return Response(userlst, status=status.HTTP_200_OK)
        else:
            payload = {"message": "No users are Found!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        payload = {}
        users_ids_in_str = request.data.get("users")
        if users_ids_in_str is not None:
            userIds = users_ids_in_str.split(",")
            userIds = [0 if userId == "" else int(userId) for userId in userIds]
            # print(userIds)
            if len(userIds) > 0:
                users = CustomUser.objects.filter(id__in=userIds)
                # print(users)
                with transaction.atomic():
                    for user in users:
                        user.is_approved = True
                        user.save()
                payload = {"message": "Users are successfully approved as Voters!"}
                return Response(payload, status=status.HTTP_200_OK)
            else:
                payload = {"message": "Please select any voters!"}
                return Response(payload, status=status.HTTP_404_NOT_FOUND)
        else:
            payload = {"message": "Please select any voters!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


class VoteView(APIView):
    def get(self, request):
        resultList = []
        oj = {}
        result = CandidatesVotes.objects.filter(is_active=True)
        if result is not None:
            for data in result:
                oj = {
                    "party": data.candidate.party_name,
                    "candidate": data.candidate.full_name,
                    "votes": data.votes,
                }
                resultList.append(oj)
            return Response(resultList, status=status.HTTP_200_OK)
        else:
            payload = {"message": "No Results Found!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        payload = {}
        candidate_votes = 0

        candidate_id = request.data.get("candidate_id")
        candidate = Candidates.objects.filter(id=candidate_id).first()

        if candidate is None:
            payload = {"message": "Please select candidate carefully to Vote!"}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        uid = request.headers.get("uid")
        candidate_votes = request.headers.get("candidate_votes", 0)
        if uid is not None:
            user = CustomUser.get_user(uid)
            vote_data = CandidatesVotes(
                candidate=candidate,
                votes=candidate_votes,
                is_active=True,
            )
            vote_data.save()
            last_vote_recored = CandidatesVotes.objects.all().latest("id")
            last_vote_recored.users.add(user)
            payload = {"message": "You have successfully given Vot."}
            return Response(payload, status=status.HTTP_200_OK)
        else:
            payload = {"message": "User is not Found!"}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


class ChagePhaseView(APIView):
    def get_phase(self, value):
        for phase in PHASES:
            if phase[0] == value:
                return phase[1]
        return "None"

    def get(self, request):
        payload = {}
        phaseOj = SystemPhases.objects.all().latest("id")
        if phaseOj is not None:
            phase_value = self.get_phase(phaseOj.phase)
            payload = {"phase": phase_value}
            return Response(payload, status=status.HTTP_200_OK)
        else:
            payload = {"message": "Phase is not Found!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        phase = request.data.get("phase")
        phaseOj = SystemPhases.objects.all().latest("id")
        if phaseOj is not None:
            phaseOj.phase = phase
            phaseOj.save()
            payload = {"message": "System Phase is Changed successfully!"}
            return Response(payload, status=status.HTTP_204_NO_CONTENT)
        else:
            payload = {"message": "Phase is not Found!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


class StatasticsDataView(APIView):
    def get(self, request):
        payload = {
            "candidates": Candidates.objects.all().count(),
            "users": CustomUser.objects.filter(is_superuser=False).count(),
            "registered_users": CustomUser.objects.filter(
                status=USER_STATUS[1][0], is_superuser=False
            ).count(),
            "unregistered_users": CustomUser.objects.filter(
                status=USER_STATUS[0][0], is_superuser=False
            ).count(),
            "approved_users": CustomUser.objects.filter(
                is_approved=True, is_superuser=False
            ).count(),
            "nonapproved_users": CustomUser.objects.filter(
                is_approved=False, is_superuser=False
            ).count(),
        }
        return Response(payload, status=status.HTTP_201_CREATED)
