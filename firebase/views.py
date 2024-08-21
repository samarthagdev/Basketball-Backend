from django.shortcuts import render
import firebase_admin
from firebase_admin import credentials, messaging
from .models import devicetoken, notificationMessage
from main_app.models import Players, Team
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from datetime import datetime

# Create your views here.

cred = credentials.Certificate("C:/Users/91928/OneDrive/Desktop/Earned Income/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
registration_tokens = []


def fire(token, title1, body1):
    registration_tokens = [token]
    message = messaging.MulticastMessage(
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                title=title1,
                body=body1,
                priority='high',
                default_sound=True,
            )
        ),
        tokens=registration_tokens,
    )
    return message


def fire1(body1, title1, token):
    registration_tokens = token
    message = messaging.MulticastMessage(
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                title=title1,
                body=body1,
                priority='high',
                default_sound=True,
            )
        ),
        tokens=registration_tokens,
    )
    return message


def individual_message(username, token, title, body, ):
    if devicetoken.objects.filter(userName=username, fcm_token=token).exists():
        d = {'type': 'normal', 'title': title, 'body': body}
        saving_mess = notificationMessage(userName=username, messages=json.dumps(d))
        saving_mess.save()
        mess = fire(token, title, body)
        response = messaging.send_multicast(mess)
        return response
    else:
        return 'no user'


def firebase_account(uni_id, firebase_token, data):
    try:
        if devicetoken.objects.filter(userName=uni_id).exists():
            account = devicetoken.objects.get(userName=uni_id)
            account.fcm_token = firebase_token
            account.log_status = True
            account.save()
            try:
                player = Players.objects.get(userName=uni_id)
                data['height'] = player.height
                data['weight'] = player.weightc
                data['dob'] = player.dob.strftime("%d-%m-%Y")
                data['gender'] = player.gender
                data['address'] = player.address
                return Response(status=status.HTTP_200_OK, data=data)
            except:
                res = individual_message(uni_id, firebase_token,
                                         'Player Account Creating',
                                         'Please Make a Player account to continue as a player, menu > player account > '
                                         'fill all the fields')
                return Response(status=status.HTTP_200_OK, data=data)
        else:
            account = devicetoken(userName=uni_id, fcm_token=firebase_token,
                                  log_status=True)
            res = individual_message(uni_id, firebase_token,
                                     'Player Account Creating',
                                     'Please Make a Player account to continue as a player, menu > player account > '
                                     'fill all the fields')
            account.save()
            return Response(status=status.HTTP_200_OK, data=data)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def firebase_team(data, team, category, owner, teamid):
    try:
        lis_token = []
        title = '{e} wants you to join the team'.format(e=team)
        for x in data:
            t = devicetoken.objects.get(userName=x['userName'])
            request_lis = json.loads(t.team_request)
            request_lis.append(teamid)
            t.team_request = json.dumps(request_lis)
            t.save()

            t1 = devicetoken.objects.get(userName=owner)
            request_player = json.loads(t1.player_request)
            if teamid in request_player:
                lis_request_player = request_player[teamid]
                lis_request_player.append(x['userName'])
            else:
                request_player[teamid] = [x['userName']]
            t1.player_request = json.dumps(request_player)
            t1.save()

            if t.log_status:
                lis_token.append(t.fcm_token)
            d = {'team': team, 'owner': owner, 'type': category, 'title': title, 'teamid': teamid}
            saving_mess = notificationMessage(userName=x['userName'], messages=json.dumps(d))
            saving_mess.save()
        mess = fire1(body1=team, title1=title, token=lis_token)
        response = messaging.send_multicast(mess)
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def firebase_join(team_id, owner, team, userName):
    try:
        token = devicetoken.objects.get(userName=owner)
        lis_token = [token.fcm_token]
        title = '{player} wants to Join your Team'.format(player=userName)
        d = {'team': team, 'userName': userName, 'type': 'join_team', 'title': title, 'team_id': team_id}
        saving_mess = notificationMessage(userName=owner, messages=json.dumps(d))
        saving_mess.save()
        mess = fire1(body1=team, title1=title, token=lis_token)
        response = messaging.send_multicast(mess)

        device = devicetoken.objects.get(userName=userName)
        team_lis = json.loads(device.team_request)
        team_lis.append(team_id)
        device.team_request = json.dumps(team_lis)
        device.save()

        device1 = devicetoken.objects.get(userName=owner)
        request_player = json.loads(device1.player_request)
        if team_id in request_player:
            lis_request_player = request_player[team_id]
            lis_request_player.append(userName)
        else:
            response[team_id] = [userName]
        device1.player_request = json.dumps(request_player)
        device1.save()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def firebase_tour(invitation, referee, tour_id, host_name, tour_name):
    try:
        referee_token = []
        title = '{h} want you to be referee in tournament'.format(h=host_name)
        for x in referee:
            dic = {'tour_name': tour_name, 'host': host_name, 'type': 'referee_tournament', 'title': title, 'tour_id': tour_id}
            device = devicetoken.objects.get(userName=x['userName'])
            referee_token.append(device.fcm_token)
            notify = notificationMessage(userName=x['userName'], messages=json.dumps(dic))
            notify.save()
        mess = fire1(body1=tour_name, title1=title, token=referee_token)
        messaging.send_multicast(mess)

        invitation_lis = []
        title = '{h} want you to participate in tournament'.format(h=host_name)
        for x in invitation:
            dic = {'tour_name': tour_name, 'host': host_name, 'type': 'team_tournament', 'title': title,
                   'tour_id': tour_id, 'team_id': x['team_id'], 'team_name': x['team_name']}
            team = Team.objects.get(team_id=x['team_id'])
            team_tour = json.loads(team.tournament)
            team_tour[tour_id] = {'status': 'pending', 'tour_name': tour_name, 'host': host_name}
            team.tournament = json.dumps(team_tour)
            team.save()
            device = devicetoken.objects.get(userName=team.owner)
            invitation_lis.append(device.fcm_token)
            notify = notificationMessage(userName=team.owner, messages=json.dumps(dic))
            notify.save()
        mess = fire1(body1=tour_name, title1=title, token=invitation_lis)
        messaging.send_multicast(mess)
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def firebase_tour_join(team_name, tour_name, team_owner, tour_owner, tour_id, team_id):
    try:
        device = devicetoken.objects.get(userName=tour_owner)
        title = '{s} wants to participate in your tournament'.format(s=team_name)
        dic = {'tour_name': tour_name, 'team_name': team_name, 'type': 'join_tournament', 'team_owner': team_owner,
               'tour_id': tour_id, 'team_id': team_id}
        notify = notificationMessage(userName=tour_owner, messages=json.dumps(dic))
        notify.save()
        mess = fire1(body1=tour_name, title1=title, token=[device.fcm_token])
        messaging.send_multicast(mess)
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def firebase_team_join(team_name, tour_name, team_owner, tour_owner, tour_id, team_id):
    try:
        device = devicetoken.objects.get(userName=tour_owner)
        title = '{h} want you to participate in tournament'.format(h=tour_owner)
        dic = {'tour_name': tour_name, 'team_name': team_name, 'type': 'team_tournament', 'team_owner': team_owner,
               'tour_id': tour_id, 'team_id': team_id}
        notify = notificationMessage(userName=team_owner, messages=json.dumps(dic))
        notify.save()
        mess = fire1(body1=tour_name, title1=title, token=[device.fcm_token])
        messaging.send_multicast(mess)
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def firebase_ref_join(tour_name, username, tour_owner, tour_id):
    try:
        title = '{h} want you to be referee in tournament'.format(h=tour_owner)
        dic = {'tour_name': tour_name, 'host': tour_owner, 'type': 'referee_tournament', 'title': title,
               'tour_id': tour_id}
        device = devicetoken.objects.get(userName=username)
        notify = notificationMessage(userName=username, messages=json.dumps(dic))
        notify.save()
        mess = fire1(body1=tour_name, title1=title, token=[device.fcm_token])
        messaging.send_multicast(mess)
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
