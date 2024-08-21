from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from .serializers import PlayerSerializer
from account.models import Otpveification1, Account
from .models import Players, Team, Tournament, Match
from datetime import datetime
import json
from firebase.views import *
import ast
# Create your views here.


@api_view(['POST'])
def creating_player(request):
    if request.method == 'POST':
        date = datetime.strptime(request.data.get('dob'), "%d-%m-%Y")
        account = Account.objects.get(userName=request.data.get('userName'))
        if Players.objects.filter(userName=request.data.get('userName')).exists():
            play_acc = Players.objects.get(userName=request.data.get('userName'))
            play_acc.userName = request.data.get('userName')
            play_acc.address = request.data.get('address')
            play_acc.dob = date
            play_acc.gender = request.data.get('gender')
            play_acc.height = request.data.get('height')
            play_acc.weight = request.data.get('weight')
            if request.data.get('pic') is not None:
                play_acc.pic = request.data.get('pic')
                account.profile_pic = request.data.get('pic')
            play_acc.save()
            if int(request.data.get('otp')) != 0:
                if Otpveification1.objects.filter(number=request.data.get('number'), otp=int(request.data.get('otp'))).exists():
                    account.number = request.data.get('number')
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            account.save()
            serializer = PlayerSerializer(play_acc, context={"request": request})
            return Response(status=status.HTTP_200_OK, data=serializer.data)

        elif account.number == request.data.get('number'):
            if request.data.get('pic') is not None:
                account.profile_pic = request.data.get('pic')
            account.save()
            reb = {'Offensive': 0, 'Defensive': 0}
            point = {'3pm': 0, '2pm': 0, 'F.T': 0, 'F.T attempt': 0, '3 attempt': 0, '2 attempt': 0}
            total_match = {'Level 1': 0, 'Level 2': 0, 'Level 3': 0, 'Level 4': 0}
            player = Players(userName=request.data.get('userName'), gender=request.data.get('gender'),
                             dob=date, address=request.data.get('address'), height=request.data.get('height'),
                             weight=request.data.get('weight'), name=account.name, pic=account.profile_pic, rebound=json.dumps(reb),
                             points=json.dumps(point), totalMatch=json.dumps(total_match))
            player.save()
            serializer = PlayerSerializer(player, context={'request': request})
            data = serializer.data
            return Response(status=status.HTTP_200_OK, data=data)

        elif Otpveification1.objects.filter(number=request.data.get('number'), otp=int(request.data.get('otp'))).exists():

            account.number = request.data.get('number')
            if request.data.get('pic') is not None:
                account.profile_pic = request.data.get('pic')
            account.save()
            reb = {'Offensive': 0, 'Defensive': 0}
            point = {'3pm': 0, '2pm': 0, 'F.T': 0, 'F.T attempt': 0, '3 attempt': 0, '2 attempt': 0}
            total_match = {'Level 1': 0, 'Level 2': 0, 'Level 3': 0, 'Level 4': 0}
            player = Players(userName=request.data.get('userName'), pic=account.profile_pic, name=account.name,
                             gender=request.data.get('gender'), dob=date, address=request.data.get('address'),
                             height=request.data.get('height'), weight=request.data.get('weight'), rebound=json.dumps(reb),
                             points=json.dumps(point), totalMatch=json.dumps(total_match))
            player.save()
            serializer = PlayerSerializer(player, context={'request': request})
            data = serializer.data
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def creating_team(request):
    if request.method == 'POST':
        list_player = request.data.get('players')
        list_player = list_player.strip("[]").split(", ")
        player = []
        for x in list_player:
            value = json.loads(x)
            player.append(value)
        s = Team.objects.count()
        teamid = 'team_{value}'.format(value=s)
        reb = {'Offensive': 0, 'Defensive': 0}
        point = {'3pm': 0, '2pm': 0, 'F.T': 0, 'F.T attempt': 0, '3 attempt': 0, '2 attempt': 0}
        total_match = {'Level 1': 0, 'Level 2': 0, 'Level 3': 0, 'Level 4': 0}
        team = Team(owner=request.data.get('ownerName'), team_name=request.data.get('teamName'),
                    address=request.data.get('address'), category=request.data.get('level'), players=json.dumps(player),
                    team_pic=request.data.get('pic'), team_id=teamid, rebound=json.dumps(reb), points=json.dumps(point),
                    totalMatch=json.dumps(total_match))
        team.save()
        return firebase_team(data=player, team=request.data.get('teamName'), teamid=teamid, owner=request.data.get('ownerName'),
                             category='createTeam',)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def joining_team(request):
    if request.method == 'POST':
        team = Team.objects.get(team_id=request.data.get('team_id'))
        return firebase_join(team_id=team.team_id, userName=request.data.get('userName'), owner=team.owner,
                             team=team.team_name)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def adding_player(request):
    if request.method == 'POST':
        team = Team.objects.get(team_id=request.data.get('team_id'))
        lis_player = json.loads(team.players)
        dic = request.data.get('player')
        lis_player.append(dic)
        team.players = json.dumps(lis_player)
        team.save()
        return firebase_team(data=[dic], team=team.team_name, teamid=team.team_id, owner=team.owner,
                             category='createTeam',)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def creating_tournament(request):
    if request.method == 'POST':
        date = datetime.strptime(request.data.get('tour_date'), "%d-%m-%Y")
        _id = 'tour_{i}'.format(i=Tournament.objects.count())
        tour = Tournament(tour_name=request.data.get('tour_name'), tour_category=request.data.get('tour_category'),
                          tour_owner=request.data.get('tour_owner'), tour_description=request.data.get('tour_description')
                          , tour_venue=request.data.get('tour_venue'), tour_referee=json.dumps(request.data.get('tour_referee')),
                          tour_date=date, tour_id=_id, tour_teams=json.dumps(request.data.get('tour_invitation')),
                          tour_registration=True, is_challenge=request.data.get('is_challenge'))
        tour.save()
        return firebase_tour(invitation=request.data.get('tour_invitation'), referee=request.data.get('tour_referee'),
                             tour_id=tour.tour_id, host_name=tour.tour_owner, tour_name=tour.tour_name)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def joining_tournament(request):
    if request.method == 'POST':
        tour = Tournament.objects.get(tour_id=request.data.get('tour_id'))
        team = Team.objects.get(team_id=request.data.get('team_id'))
        tour_teams = json.loads(tour.tour_teams)
        tour_teams.append({'team_name': team.team_name, 'pic': team.team_pic.name, 'team_id': team.team_id,
                           'status': 'pending'})
        tour.tour_teams = json.dumps(tour_teams)
        tour.save()
        team_tour = json.loads(team.tournament)
        team_tour[tour.tour_id] = {'status': 'pending', 'tour_name': tour.tour_name, 'host': tour.tour_owner}
        team.tournament = json.dumps(team_tour)
        team.save()
        return firebase_tour_join(team_name=team.team_name, team_id=team.team_id, team_owner=team.owner,
                                  tour_name=tour.tour_name, tour_id=tour.tour_id, tour_owner=tour.tour_owner)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sending_request_tournament(request):
    if request.method == 'POST':
        data = request.data.get('data')
        tour_id = request.data.get('tour_id')
        tour = Tournament.objects.get(tour_id=tour_id)
        if request.data.get('type') == 'Teams':
            tour_teams = json.loads(tour.tour_teams)
            tour_teams.append(data)
            tour.tour_teams = json.dumps(tour_teams)
            tour.save()
            team = Team.objects.get(team_id=data['team_id'])
            team_tour = json.loads(team.tournament)
            team_tour[tour_id] = {'status': 'pending', 'tour_name': tour.tour_name, 'host': tour.tour_owner}
            team.tournament = json.dumps(team_tour)
            team.save()
            return firebase_team_join(team_name=team.team_name, tour_name=tour.tour_name, team_owner=team.owner
                                      , tour_owner=tour.tour_owner, tour_id=tour.tour_id, team_id=team.team_id)
        elif request.data.get('type') == 'Referee':
            ref = json.loads(tour.tour_referee)
            ref.append(data)
            tour.tour_referee = json.dumps(ref)
            tour.save()
            return firebase_ref_join(tour_name=tour.tour_name, username=data['userName'], tour_owner=tour.tour_owner,
                                     tour_id=tour.tour_id)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def uploading_fixture(request):
    if request.method == 'POST':
        tour = Tournament.objects.get(tour_id=request.data.get('tour_id'))
        tour.tour_fixture = request.data.get('pic')
        tour.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def adding_matches(request):
    if request.method == 'POST':
        data = request.data
        lis_match = data['match_details']
        for x in lis_match:
            tour = Tournament.objects.get(tour_id=data['tour_id'])
            last_match = Match.objects.all().last()
            if last_match is None:
                _id = 'match_0'
            else:
                id_no = int(last_match.match_id.strip("match_"))
                _id = 'match_{s}'.format(s=id_no+1)
            add_date_time = request.data['date']+' '+x['time']
            date = datetime.strptime(add_date_time, '%d-%m-%Y %H:%M %p')
            match = Match(match_between=json.dumps(x), tour_id=data['tour_id'], match_id=_id, date=date, match_venue=tour.tour_venue)
            match.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def changes(request):
#     player = Players.objects.all()
#     team =Team.objects.all()
#     for x in player:
#         x.rebound = json.dumps({"Offensive": 0, "Defensive": 0})
#         x.points = json.dumps({"3pm": 0, "2pm": 0, "F.T": 0, "F.T attempt": 0, "3 attempt": 0, "2 attempt": 0})
#         x.totalMatch = json.dumps({"Level 1": 0, "Level 2": 0, "Level 3": 0, "Level 4": 0})
#         x.steal = 0
#         x.assist = 0
#         x.block = 0
#         x.save()
#     for y in team:
#         y.rebound = json.dumps({"Offensive": 0, "Defensive": 0})
#         y.points = json.dumps({"3pm": 0, "2pm": 0, "F.T": 0, "F.T attempt": 0, "3 attempt": 0, "2 attempt": 0})
#         y.totalMatch = json.dumps({"Level 1": 0, "Level 2": 0, "Level 3": 0, "Level 4": 0})
#         y.steal = 0
#         y.assist = 0
#         y.block = 0
#         y.save()
#     return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def changes(request):
    a = Match.objects.all()
    for x in a:
        y = Tournament.objects.get(tour_id= x.tour_id)
        x.match_venue = y.tour_venue
        x.save()
    return Response(status=status.HTTP_200_OK)