# chat/consumers.py
from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Players, Team, Tournament, Match, TeamRanking, PlayerRanking, Youtube
from account.models import Account
from .serializers import MatchSerializer
from django.db.models import Q
from firebase.models import devicetoken, notificationMessage
import ast
from django.core.paginator import Paginator
from channels.layers import get_channel_layer
from datetime import datetime
channel_layer = get_channel_layer()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_name = self.scope['user']
        self.room_group_name = 'chat_%s' % self.room_name
        self.room_group_name3 = ''
        self.room_group_name2 = ''
        self.homepage = []
        self.live_match = []
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if ('add_another_group_by_ref' == message['type'] and self.room_group_name2 == '') or ('Getting Full Match Information' == message['type'] and self.room_group_name2 == ''):
            self.room_group_name2 = 'chat_%s' % message['data'] + '_ref'
            await self.channel_layer.group_add(
                self.room_group_name2,
                self.channel_name
            )
            self.room_group_name3 = 'chat_%s' % message['data']
            await self.channel_layer.group_add(
                self.room_group_name3,
                self.channel_name
            )
        if 'add_another_group' == message['type']:
            self.room_group_name3 = 'chat_%s' % message['data']
            await self.channel_layer.group_add(
                self.room_group_name3,
                self.channel_name
            )

        mess = await self.handling(message)
        mess1 = message['type']
        # Send message to room group
        if message['type'] == 'add_another_group_by_ref':
            data = mess["another route started"]
            await match_started_by_ref(match_id=data["match_id"], status=data["status"],
                                       a_5=data["team_a_player_stats"],
                                       b_5=data["team_b_player_stats"], quarter=data['quarter'],
                                       id=message['ref_id'])
        elif message['type'] == 'scoring':
            await match_scoring(match_id=mess['match_id'], a_5=mess["team_a_player_stats"],
                                b_5=mess["team_b_player_stats"], a1=mess['team_a_1'], a2=mess['team_a_2'], a3=mess['team_a_3'],
                                b1=mess['team_b_1'], b2=mess['team_b_2'], b3=mess['team_b_3'])

        elif message['type'] == 'close group by ref' and self.room_group_name2 != '':
            await self.channel_layer.group_discard(
                self.room_group_name3,
                self.channel_name
            )
            await self.channel_layer.group_discard(
                self.room_group_name2,
                self.channel_name
            )
            self.room_group_name2 = ''
            self.room_group_name3 = ''
        elif message['type'] == 'close group by player' and self.room_group_name3 != '':
            await self.channel_layer.group_discard(
                self.room_group_name3,
                self.channel_name
            )
            self.room_group_name3 = ''
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': mess,
                    'from': mess1,
                }
            )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        message1 = event['from']
        # Send message to WebSocket
        # print(message)
        await self.send(text_data=json.dumps({
            'message': message,
            'from': message1
        }))
        if message1 == 'close':
            await self.close(1000)

    @database_sync_to_async
    def handling(self, message):
        data = message['data']
        content = message['type']
        if content == 'search_player':
            data = data.lower()
            query = list(Players.objects.filter(Q(userName__startswith=data) | Q(address__istartswith=data)
                                                | Q(name__istartswith=data)).values('userName', 'pic'))
            return query
        elif content == 'close':
            statusupdate = devicetoken.objects.get(userName=self.room_name)
            statusupdate.log_status = False
            statusupdate.save()
            return 'Done'
        elif content == 'notification':
            notification_mess = list(notificationMessage.objects.filter(userName=self.room_name).order_by('-id')
                                     .values('messages', 'id'))

            return notification_mess
        elif content == 'notification response':
            res = message['response']
            id_mess = message['pk']
            team = Team.objects.get(team_id=data['teamid'])
            lis_player = []
            players = json.loads(team.players)
            userName = self.scope['user'].userName
            for x in players:
                if x['userName'] == userName:
                    if res == 'accept':
                        x['status'] = res
                        player = Players.objects.get(userName=userName)
                        s = player.teams
                        if s == '[]':
                            s = [{'id': data['teamid'], 'pic':team.team_pic.name, 'team_name':team.team_name}]
                        else:
                            s1 = json.loads(s)
                            s1.append({'id': data['teamid'], 'pic': team.team_pic.name, 'team_name': team.team_name})
                            s = s1
                        player.teams = json.dumps(s)
                        player.save()
                    else:
                        device = devicetoken.objects.get(userName=userName)
                        team_lis = json.loads(device.team_request)
                        team_lis.remove(team.team_id)
                        device.team_request = json.dumps(team_lis)
                        device.save()

                        device1 = devicetoken.objects.get(userName=team.owner)
                        player_lis = json.loads(device1.player_request)
                        player_lis[team.team_id].remove(userName)
                        device1.player_request = json.dumps(player_lis)
                        device1.save()
                        continue
                lis_player.append(x)
            team.players = json.dumps(lis_player)
            team.save()
            notificationMessage.objects.get(pk=id_mess).delete()
            return 'Done'
        elif content == 'search_team':
            data = data.lower()
            query = list(Team.objects.filter(Q(team_name__istartswith=data) | Q(address__istartswith=data)
                                             | Q(owner__startswith=data)).values('team_name', 'team_pic', 'team_id'))
            return query
        elif content == 'search_normal':
            data = data.lower()
            query = list(Account.objects.filter(Q(userName__startswith=data) | Q(name__istartswith=data))
                         .values('userName', 'profile_pic'))
            return query
        elif content == 'profile':
            try:
                player = list(Players.objects.filter(userName=data).values())[0]
                player['teams'] = json.loads(player['teams'])
                player['totalMatch'] = ast.literal_eval(player['totalMatch'])
                player['rebound'] = ast.literal_eval(player['rebound'])
                player['points'] = ast.literal_eval(player['points'])
                player['name'] = player['name'].capitalize()
                player['dob'] = player['dob'].strftime("%Y-%m-%d")
                return player
            except:
                account = list(Account.objects.filter(userName=data).values('profile_pic', 'name', 'userName'))[0]
                account['name'] = account['name'].capitalize()
                account['pic'] = account['profile_pic']
                return account
        elif content == 'team_profile':
            team = list(Team.objects.filter(team_id=data).values('team_name', 'owner', 'players', 'category', 'address',
                                                                 'totalMatch', 'points', 'assist', 'block', 'rebound',
                                                                 'steal'))[0]
            team['players'] = json.loads(team['players'])
            team['totalMatch'] = ast.literal_eval(team['totalMatch'])
            team['rebound'] = ast.literal_eval(team['rebound'])
            team['points'] = ast.literal_eval(team['points'])
            team['team_name'] = team['team_name'].capitalize()
            return team
        elif content == 'my_team':
            player = list(Players.objects.filter(userName=data).values('teams'))
            own_team = list(Team.objects.filter(owner=data).values('team_id', 'team_name', 'team_pic'))
            if len(player) > 0:
                player = player[0]
                player['teams'] = json.loads(player['teams'])
                dic = {'player': player['teams'], 'own_team': own_team}
            else:
                dic = {'player': player, 'own_team': own_team}
            return dic
        elif content == 'pending_request':
            pending = list(devicetoken.objects.filter(userName=data).values('team_request'))[0]
            return json.loads(pending['team_request'])
        elif content == 'pending_request1':
            pending = list(devicetoken.objects.filter(userName=data).values('player_request'))[0]
            return json.loads(pending['player_request'])[message['team']]
        elif content == 'notification response1':
            team = Team.objects.get(team_id=data['team_id'])
            player = Players.objects.get(userName=data['userName'])
            if message['response'] == 'accept':
                team_player = json.loads(team.players)
                dic = {'userName': data['userName'], 'pic': player.pic.name, 'status': 'accept'}
                team_player.append(dic)
                team.players = json.dumps(team_player)
                lis_player = json.loads(player.teams)
                if lis_player is []:
                    player.teams = json.dumps({'id': data['team_id'], 'team_name': team.team_name,
                                               'pic': team.team_pic.name})
                else:
                    dic1 = {'id': data['team_id'], 'team_name': team.team_name, 'pic': team.team_pic.name}
                    lis_player.append(dic1)
                    player.teams = json.dumps(lis_player)
                player.save()
                team.save()
            else:
                device = devicetoken.objects.get(userName=player.userName)
                team_lis = json.loads(device.team_request)
                team_lis.remove(team.team_id)
                device.team_request = json.dumps(team_lis)
                device.save()

                device1 = devicetoken.objects.get(userName=team.owner)
                player_lis = json.loads(device1.player_request)
                player_lis[team.team_id].remove(player.userName)
                device1.player_request = json.dumps(player_lis)
                device1.save()
            notificationMessage.objects.get(pk=message['pk']).delete()
            return 'Done'
        elif content == 'search_tournament':
            tour = list(Tournament.objects.filter(Q(tour_name__istartswith=data) |
                                                  Q(tour_venue__istartswith=data) |
                                                  Q(tour_owner__startswith=data) and Q(tour_registration=
                                                                                       message['data1']))
                        .values('tour_id', 'tour_owner', 'tour_name'))
            return tour
        elif content == 'notification response 2':
            tour = Tournament.objects.get(tour_id=data['tour_id'])
            if tour.tour_registration:
                lis_teams = json.loads(tour.tour_teams)
                lis_teams_1 = []
                team = Team.objects.get(team_id=data['team_id'])
                team_tour = json.loads(team.tournament)
                for x in lis_teams:
                    if x['team_id'] == data['team_id']:
                        if message['response'] == 'accept':
                            x['status'] = 'accept'
                            team_tour[data['tour_id']]['status'] = 'accept'
                            team.tournament = json.dumps(team_tour)
                            team.save()
                        else:
                            del team_tour[data['tour_id']]
                            team.tournament = json.dumps(team_tour)
                            team.save()
                            continue
                    lis_teams_1.append(x)
                tour.tour_teams = json.dumps(lis_teams_1)
                tour.save()
            notificationMessage.objects.get(pk=message['pk']).delete()
            return 'Done'
        elif content == 'notification response 3':
            tour = Tournament.objects.get(tour_id=data['tour_id'])
            lis_referee = json.loads(tour.tour_referee)
            lis_referee_1 = []
            userName = self.scope['user'].userName
            for x in lis_referee:
                if x['userName'] == userName:
                    if message['response'] == 'accept':
                        x['status'] = 'accept'
                    else:
                        continue
                lis_referee_1.append(x)
            tour.tour_referee = json.dumps(lis_referee_1)
            tour.save()
            player = Players.objects.get(userName=userName)
            lis_player_referee = json.loads(player.referee)
            lis_player_referee.append({'tour_id': tour.tour_id, 'tour_name': tour.tour_name, 'host': tour.tour_owner})
            player.referee = json.dumps(lis_player_referee)
            player.save()
            notificationMessage.objects.get(pk=message['pk']).delete()
            return 'Done'
        elif content == 'Tour Details':
            tour = list(Tournament.objects.filter(tour_id=data).values())[0]
            tour['tour_date'] = tour['tour_date'].strftime("%Y-%m-%d")
            tour['tour_referee'] = json.loads(tour['tour_referee'])
            tour['tour_teams'] = json.loads(tour['tour_teams'])
            return tour
        elif content == 'Get Teams':
            team = list(Team.objects.filter(owner=data).values('team_id', 'team_name'))
            return team
        elif content == 'pending tour teams':
            team = list(Team.objects.filter(team_id=data).values('tournament'))[0]
            return list(json.loads(team['tournament']).keys())
        elif content == 'notification response 4':
            tour = Tournament.objects.get(tour_id=data['tour_id'])
            if tour.tour_registration:
                team = Team.objects.get(team_id=data['team_id'])
                tour_teams = json.loads(tour.tour_teams)
                lis_tour_teams = []
                for x in tour_teams:
                    if x['team_id'] == data['team_id']:
                        team_tour = json.loads(team.tournament)
                        if message['response'] == 'accept':
                            x['status'] = 'accept'
                            team_tour[tour.tour_id]['status'] = 'accept'
                            team.tournament = json.dumps(team_tour)
                            team.save()
                        else:
                            del team_tour[data['tour_id']]
                            team.tournament = json.dumps(team_tour)
                            team.save()
                            continue
                    lis_tour_teams.append(x)
                tour.tour_teams = json.dumps(lis_tour_teams)
                tour.save()
            notificationMessage.objects.get(pk=message['pk']).delete()
            return 'Done'
        elif content == 'Get Joined Tournament':
            player = Players.objects.get(userName=data)
            player_team = json.loads(player.teams)
            lis_tour = []
            for x in player_team:
                team = Team.objects.get(team_id=x['id'])
                team_tour = json.loads(team.tournament)
                if team_tour is not {}:
                    lis_tour.append(team_tour)
            return lis_tour
        elif content == 'Get Tournament by Host':
            tour = list(Tournament.objects.filter(tour_owner=data).values('tour_id', 'tour_name', 'tour_category'))
            return tour
        elif content == 'pending tour request':
            tour = list(Tournament.objects.filter(tour_id=data).values('tour_teams', 'tour_referee'))[0]
            tour['tour_teams'] = json.loads(tour['tour_teams'])
            tour['tour_referee'] = json.loads(tour['tour_referee'])
            return tour
        elif content == 'stop registration':
            tour = Tournament.objects.get(tour_id=data)
            if 'extra_data' in message:
                tour.tour_registration = True
                tour.save()
                return {}
            tour.tour_registration = False
            tour.save()
            return {'teams': json.loads(tour.tour_teams), 'registration': tour.tour_registration}
        elif content == 'registration check':
            tour = Tournament.objects.get(tour_id=data)
            if tour.tour_registration:
                return {}
            return {'teams': json.loads(tour.tour_teams), 'registration': tour.tour_registration,
                    'fixture': tour.tour_fixture.name}
        elif content == 'Get Tournament by Referee':
            player = list(Players.objects.filter(userName=data).values('referee'))[0]
            return json.loads(player['referee'])
        elif content == 'Get Matches':
            match = list(Match.objects.filter(tour_id=data).order_by('date').values('match_id', 'match_between'))
            # convert match_between
            return match
        elif content == 'Get teams for matches':
            tour = Tournament.objects.get(tour_id=data)
            tour_teams = json.loads(tour.tour_teams)
            lis_team = []
            lis_team_name = []
            for x in tour_teams:
                if x['status'] == 'accept':
                    lis_team.append(x)
                    lis_team_name.append(x['team_name'])
            return {'lis_team': lis_team, 'lis_team_name': lis_team_name}
        elif content == 'delete existing match':
            Match.objects.get(match_id=data).delete()
            return 'Done'
        # I have changed from hear
        elif content == 'Getting Full Match Information':
            match = list(Match.objects.filter(match_id=data).values('tour_id', 'match_between', 'team_a_player_stats',
                                                                    'team_b_player_stats', 'status', 'quarter'))[0]
            match_between = json.loads(match['match_between'])
            tour = list(Tournament.objects.filter(tour_id=match['tour_id']).values('tour_category'))[0]
            team_a = list(Team.objects.filter(team_id=match_between['team A']['team_id']).values('players'))[0]
            team_b = list(Team.objects.filter(team_id=match_between['team B']['team_id']).values('players'))[0]
            return {'team_a_player': json.loads(team_a['players']), 'team_b_player': json.loads(team_b['players']),
                    'category': tour['tour_category'], 'team_a_player_playing': json.loads(match['team_a_player_stats'])
                    , 'team_b_player_playing': json.loads(match['team_b_player_stats']), 'status': match['status'],
                    'quarter': match['quarter']}
        elif content == 'add lineup for match':
            match = Match.objects.get(match_id=message['match_id'])
            match.team_b_player_stats = json.dumps(data['team_b_player_playing'])
            match.team_a_player_stats = json.dumps(data['team_a_player_playing'])
            match.save()
            return 'Done'
        elif content == 'All Matches of Tour':
            match = list(Match.objects.filter(tour_id=data).order_by('date').values('match_between', 'match_id',
                                                                                    'date', 'match_venue'))
            serializer = MatchSerializer(match, many=True)
            return serializer.data
        elif content == 'add_another_group_by_ref':
            match = Match.objects.get(match_id=data)
            if match.status == 'upcoming' and message['extra_data'] == 'live':
                match.status = 'live'
                match.save()
            elif message['extra_data'] == 'end':
                match.status = 'end'
                tour = Tournament.objects.get(tour_id=match.tour_id)
                match.save()
                team_a = json.loads(match.team_a_player_stats)
                team_b = json.loads(match.team_b_player_stats)
                lis_a_user = list(team_a.keys())
                lis_b_user = list(team_b.keys())
                for x in lis_a_user:
                    player = Players.objects.get(userName=x)
                    player.assist = player.assist + team_a[x]['assist']
                    player.block = player.block + team_a[x]['block']
                    player.steal = player.steal + team_a[x]['steal']
                    player_rebound = json.loads(player.rebound)
                    player_rebound["Offensive"] = player_rebound["Offensive"]+team_a[x]['rebound']['Offensive']
                    player_rebound["Defensive"] = player_rebound["Defensive"]+team_a[x]['rebound']['Defensive']
                    player.rebound = json.dumps(player_rebound)
                    player_point = json.loads(player.points)
                    player_point['3pm'] = player_point['3pm']+team_a[x]['points']['3pm']
                    player_point['2pm'] = player_point['2pm'] + team_a[x]['points']['2pm']
                    player_point['F.T'] = player_point['F.T'] + team_a[x]['points']['F.T']
                    player_point['3 attempt'] += team_a[x]['points']['3 attempt']
                    player_point['2 attempt'] += team_a[x]['points']['2 attempt']
                    player_point['F.T attempt'] += team_a[x]['points']['F.T attempt']
                    player.points = json.dumps(player_point)
                    total_match = json.loads(player.totalMatch)
                    if tour.is_challenge:
                        total_match['Level 1'] += 1
                    else:
                        total_match['Level 2'] += 1
                    player.totalMatch = json.dumps(total_match)
                    player.save()
                    player_rank_make_id = match.tour_id + '__' + x
                    total_rebound_points = (team_a[x]['rebound']['Offensive'] * 2) + team_a[x]['rebound']['Defensive']
                    total_score_points = (team_a[x]['points']['3pm'] * 3)+(team_a[x]['points']['2pm'] * 2)+team_a[x]['points']['F.T']
                    if PlayerRanking.objects.filter(player_rank_id=player_rank_make_id).exists():
                        player_rank = PlayerRanking.objects.get(player_rank_id=player_rank_make_id)
                        player_rank.assist += team_a[x]['assist']
                        player_rank.block += team_a[x]['block']
                        player_rank.steal += team_a[x]['steal']
                        player_rank.rebound += total_rebound_points
                        player_rank.points += total_score_points
                        player_rank.save()
                    else:
                        player_rank = PlayerRanking(player_rank_id=player_rank_make_id, player_name=x,
                                                    steal=team_a[x]['steal'], block=team_a[x]['block'],
                                                    assist=team_a[x]['assist'], rebound=total_rebound_points,
                                                    points=total_score_points)
                        player_rank.save()

                for x in lis_b_user:
                    player = Players.objects.get(userName=x)
                    player.assist = player.assist + team_b[x]['assist']
                    player.block = player.block + team_b[x]['block']
                    player.steal = player.steal + team_b[x]['steal']
                    player_rebound = json.loads(player.rebound)
                    player_rebound["Offensive"] = player_rebound["Offensive"]+team_b[x]['rebound']['Offensive']
                    player_rebound["Defensive"] = player_rebound["Defensive"]+team_b[x]['rebound']['Defensive']
                    player.rebound = json.dumps(player_rebound)
                    player_point = json.loads(player.points)
                    player_point['3pm'] = player_point['3pm']+team_b[x]['points']['3pm']
                    player_point['2pm'] = player_point['2pm'] + team_b[x]['points']['2pm']
                    player_point['F.T'] = player_point['F.T'] + team_b[x]['points']['F.T']
                    player_point['3 attempt'] += team_b[x]['points']['3 attempt']
                    player_point['2 attempt'] += team_b[x]['points']['2 attempt']
                    player_point['F.T attempt'] += team_b[x]['points']['F.T attempt']
                    player.points = json.dumps(player_point)
                    total_match = json.loads(player.totalMatch)
                    if tour.is_challenge:
                        total_match['Level 1'] += 1
                    else:
                        total_match['Level 2'] += 1
                    player.totalMatch = json.dumps(total_match)
                    player.save()
                    player_rank_make_id = match.tour_id + '__' + x
                    total_rebound_points = (team_b[x]['rebound']['Offensive'] * 2) + team_b[x]['rebound']['Defensive']
                    total_score_points = (team_b[x]['points']['3pm'] * 3) + (team_b[x]['points']['2pm'] * 2) + team_b[x]['points']['F.T']
                    if PlayerRanking.objects.filter(player_rank_id=player_rank_make_id).exists():
                        player_rank = PlayerRanking.objects.get(player_rank_id=player_rank_make_id)
                        player_rank.assist += team_b[x]['assist']
                        player_rank.block += team_b[x]['block']
                        player_rank.steal += team_b[x]['steal']
                        player_rank.rebound += total_rebound_points
                        player_rank.points += total_score_points
                        player_rank.save()
                    else:
                        player_rank = PlayerRanking(player_rank_id=player_rank_make_id, player_name=x,
                                                    steal=team_b[x]['steal'], block=team_b[x]['block'],
                                                    assist=team_b[x]['assist'], rebound=total_rebound_points,
                                                    points=total_score_points)
                        player_rank.save()

                match_between = json.loads(match.match_between)
                team_A = Team.objects.get(team_id=match_between['team A']['team_id'])
                team_A.assist += match.team_a_assist
                team_A.steal += match.team_a_steal
                team_A.block += match.team_a_block
                team_A_rebound = json.loads(team_A.rebound)
                team_A_rebound['Offensive'] = team_A_rebound['Offensive'] + match.team_a_offensive_rebound
                team_A_rebound['Defensive'] = team_A_rebound['Defensive'] + match.team_a_defensive_rebound
                team_A.rebound = json.dumps(team_A_rebound)
                team_A_points = json.loads(team_A.points)
                team_A_points['3pm'] += match.team_a_3
                team_A_points['2pm'] += match.team_a_2
                team_A_points['F.T'] += match.team_a_1
                team_A_points['3 attempt'] += match.team_a_3_attempt
                team_A_points['2 attempt'] += match.team_a_2_attempt
                team_A_points['F.T attempt'] += match.team_a_1_attempt
                team_A.points = json.dumps(team_A_points)
                team_A_match = json.loads(team_A.totalMatch)
                if tour.is_challenge:
                    team_A_match['Level 1'] += 1
                else:
                    team_A_match['Level 2'] += 1
                team_A.totalMatch = json.dumps(team_A_match)
                team_A.save()
                team_rank_make_id = match.tour_id + '__' + team_A.team_id
                team_rank_a_rebound = (match.team_a_offensive_rebound*2) + match.team_a_defensive_rebound
                team_rank_a_points = (match.team_a_3*3)+(match.team_a_2*2)+match.team_a_1
                if TeamRanking.objects.filter(team_rank_id=team_rank_make_id).exists():
                    team_rank = TeamRanking.objects.get(team_rank_id=team_rank_make_id)
                    team_rank.assist += match.team_a_assist
                    team_rank.block += match.team_a_block
                    team_rank.steal += match.team_a_steal
                    team_rank.rebound += team_rank_a_rebound
                    team_rank.points += team_rank_a_points
                    team_rank.save()
                else:
                    team_rank = TeamRanking(team_rank_id=team_rank_make_id, team_name=team_A.team_name,
                                            steal=match.team_a_steal, block=match.team_a_block,
                                            assist=match.team_a_assist, rebound=team_rank_a_rebound,
                                            points=team_rank_a_points)
                    team_rank.save()

                team_B = Team.objects.get(team_id=match_between['team B']['team_id'])
                team_B.assist += match.team_b_assist
                team_B.steal += match.team_b_steal
                team_B.block += match.team_b_block
                team_B_rebound = json.loads(team_B.rebound)
                team_B_rebound['Offensive'] = team_B_rebound['Offensive'] + match.team_b_offensive_rebound
                team_B_rebound['Defensive'] = team_B_rebound['Defensive'] + match.team_b_defensive_rebound
                team_B.rebound = json.dumps(team_B_rebound)
                team_B_points = json.loads(team_B.points)
                team_B_points['3pm'] += match.team_b_3
                team_B_points['2pm'] += match.team_b_2
                team_B_points['F.T'] += match.team_b_1
                team_B_points['3 attempt'] += match.team_b_3_attempt
                team_B_points['2 attempt'] += match.team_b_2_attempt
                team_B_points['F.T attempt'] += match.team_b_1_attempt
                team_B.points = json.dumps(team_B_points)
                team_B_match = json.loads(team_B.totalMatch)
                if tour.is_challenge:
                    team_B_match['Level 1'] += 1
                else:
                    team_B_match['Level 2'] += 1
                team_B.totalMatch = json.dumps(team_B_match)
                team_B.save()
                team_rank_make_id = match.tour_id + '__' + team_B.team_id
                team_rank_b_rebound = (match.team_b_offensive_rebound * 2) + match.team_b_defensive_rebound
                team_rank_b_points = (match.team_b_3 * 3) + (match.team_b_2 * 2) + match.team_b_1
                if TeamRanking.objects.filter(team_rank_id=team_rank_make_id).exists():
                    team_rank = TeamRanking.objects.get(team_rank_id=team_rank_make_id)
                    team_rank.assist += match.team_b_assist
                    team_rank.block += match.team_b_block
                    team_rank.steal += match.team_b_steal
                    team_rank.rebound += team_rank_b_rebound
                    team_rank.points += team_rank_b_points
                    team_rank.save()
                else:
                    team_rank = TeamRanking(team_rank_id=team_rank_make_id, team_name=team_B.team_name,
                                            steal=match.team_b_steal, block=match.team_b_block,
                                            assist=match.team_b_assist, rebound=team_rank_b_rebound,
                                            points=team_rank_b_points)
                    team_rank.save()

            elif message['extra_data'] == 'time out':
                match.status = 'time out'
                match.save()
            elif match.status == 'time out' and message['extra_data'] == 'live':
                match.status = 'live'
                match.save()
            elif message['extra_data'] == 'quarter':
                match.quarter = message['no']
                match.save()
            elif message['extra_data'] == 'substitution':
                lis_username = []
                if 'team_a_player_stats' in message:
                    playing = message['team_a_player_stats']
                    for x in playing:
                        lis_username.append(x['username'])
                    team = json.loads(match.team_a_player_stats)
                else:
                    playing = message['team_b_player_stats']
                    for x in playing:
                        lis_username.append(x['username'])
                    team = json.loads(match.team_b_player_stats)
                team_lis = list(team.keys())
                for x in team_lis:
                    if x in lis_username:
                        user = team[x]
                        user['playing'] = 'in'
                        user['no.'] = playing[lis_username.index(x)]['no.']
                        user['username'] = x
                        team[x] = user
                    else:
                        user = team[x]
                        user['playing'] = 'out'
                        team[x] = user
                if 'team_a_player_stats' in message:
                    match.team_a_player_stats = json.dumps(team)
                else:
                    match.team_b_player_stats = json.dumps(team)
                match.save()
            return {"another route started": {'match_id': match.match_id, 'status': match.status,
                                              'team_a_player_stats': json.loads(match.team_a_player_stats),
                                              'team_b_player_stats': json.loads(match.team_b_player_stats),
                                              'quarter': match.quarter}}
        elif content == 'add_another_group':
            match = list(Match.objects.filter(match_id=data).values('team_a_1', 'team_a_2', 'team_a_3', 'team_b_1',
                                                                    'team_b_2', 'team_b_3', 'team_b_player_stats',
                                                                    'team_b_assist', 'team_b_block', 'team_b_steal',
                                                                    'team_a_assist', 'team_a_block', 'team_a_steal',
                                                                    'team_b_offensive_rebound', 'team_b_defensive_rebound',
                                                                    'team_a_offensive_rebound', 'team_a_defensive_rebound',
                                                                    'team_a_3_attempt', 'team_a_2_attempt', 'team_a_1_attempt',
                                                                    'team_b_3_attempt', 'team_b_2_attempt', 'team_b_1_attempt',
                                                                    'team_a_player_stats', 'status', 'quarter'))[0]

            match['team_a_player_stats'] = json.loads(match['team_a_player_stats'])
            match['team_b_player_stats'] = json.loads(match['team_b_player_stats'])
            return match
        elif content == 'scoring':
            match = Match.objects.get(match_id=data)
            if 'team_a_player_stats' in message and match.status != 'end':
                team = json.loads(match.team_a_player_stats)
                if message['extra_data'] == 'offensive rebound':
                    previous_data = team[message['team_a_player_stats']]['rebound']['Offensive']
                    team[message['team_a_player_stats']]['rebound']['Offensive'] = message['value']
                    nu = match.team_a_offensive_rebound - previous_data
                    match.team_a_offensive_rebound = nu + message['value']
                    match.team_a_player_stats = json.dumps(team)
                    match.save()
                elif message['extra_data'] == 'defensive rebound':
                    previous_data = team[message['team_a_player_stats']]['rebound']['Defensive']
                    team[message['team_a_player_stats']]['rebound']['Defensive'] = message['value']
                    nu = match.team_a_defensive_rebound - previous_data
                    match.team_a_defensive_rebound = nu + message['value']
                    match.team_a_player_stats = json.dumps(team)
                    match.save()
                elif message['extra_data'] == 'points':
                    if '3pm' == message['team_a_player_stats']:
                        team[message['username']]['points']['3 attempt'] += 1
                        match.team_a_3_attempt = match.team_a_3_attempt+1
                        match.team_a_3 = match.team_a_3+1
                    elif '2pm' == message['team_a_player_stats']:
                        team[message['username']]['points']['2 attempt'] += 1
                        match.team_a_2_attempt = match.team_a_2_attempt+1
                        match.team_a_2 = match.team_a_2+1
                    elif 'F.T' == message['team_a_player_stats']:
                        team[message['username']]['points']['F.T attempt'] += 1
                        match.team_a_1_attempt = match.team_a_1_attempt+1
                        match.team_a_1 = match.team_a_1+1
                    team[message['username']]['points'][message['team_a_player_stats']] += 1
                    if message['team_a_player_stats'] == '3 attempt':
                        match.team_a_3_attempt = match.team_a_3_attempt+1
                    elif message['team_a_player_stats'] == '2 attempt':
                        match.team_a_2_attempt = match.team_a_2_attempt+1
                    elif message['team_a_player_stats'] == 'F.T attempt':
                        match.team_a_1_attempt = match.team_a_1_attempt+1
                    match.team_a_player_stats = json.dumps(team)
                    match.save()
                else:
                    previous_value = team[message['team_a_player_stats']][message['extra_data']]
                    team[message['team_a_player_stats']][message['extra_data']] = message['value']
                    match.team_a_player_stats = json.dumps(team)
                    if message['extra_data'] == 'steal':
                        nu = match.team_a_steal - previous_value
                        match.team_a_steal = nu + message['value']
                    elif message['extra_data'] == 'block':
                        nu = match.team_a_block - previous_value
                        match.team_a_block = nu + message['value']
                    elif message['extra_data'] == 'assist':
                        nu = match.team_a_assist - previous_value
                        match.team_a_assist = nu + message['value']
                    match.save()
            elif match.status != 'end':
                team = json.loads(match.team_b_player_stats)
                if message['extra_data'] == 'offensive rebound':
                    previous_data = team[message['team_b_player_stats']]['rebound']['Offensive']
                    team[message['team_b_player_stats']]['rebound']['Offensive'] = message['value']
                    nu = match.team_b_offensive_rebound - previous_data
                    match.team_b_offensive_rebound = nu + message['value']
                    match.team_b_player_stats = json.dumps(team)
                    match.save()
                elif message['extra_data'] == 'defensive rebound':
                    previous_data = team[message['team_b_player_stats']]['rebound']['Defensive']
                    team[message['team_b_player_stats']]['rebound']['Defensive'] = message['value']
                    nu = match.team_b_defensive_rebound - previous_data
                    match.team_b_defensive_rebound = nu + message['value']
                    match.team_b_player_stats = json.dumps(team)
                    match.save()
                elif message['extra_data'] == 'points':
                    if '3pm' == message['team_b_player_stats']:
                        team[message['username']]['points']['3 attempt'] += 1
                        match.team_b_3_attempt = match.team_b_3_attempt+1
                        match.team_b_3 += 1
                    elif '2pm' == message['team_b_player_stats']:
                        team[message['username']]['points']['2 attempt'] += 1
                        match.team_b_2_attempt = match.team_b_2_attempt+1
                        match.team_b_2 = match.team_b_2+1
                    elif 'F.T' == message['team_b_player_stats']:
                        team[message['username']]['points']['F.T attempt'] += 1
                        match.team_b_1_attempt = match.team_b_1_attempt+1
                        match.team_b_1 = match.team_b_1+1
                    team[message['username']]['points'][message['team_b_player_stats']] += 1
                    if message['team_b_player_stats'] == '3 attempt':
                        match.team_b_3_attempt = match.team_b_3_attempt+1
                    elif message['team_b_player_stats'] == '2 attempt':
                        match.team_b_2_attempt = match.team_b_2_attempt+1
                    elif message['team_b_player_stats'] == 'F.T attempt':
                        match.team_b_1_attempt = match.team_b_1_attempt+1
                    match.team_b_player_stats = json.dumps(team)
                    match.save()
                else:
                    previous_value = team[message['team_b_player_stats']][message['extra_data']]
                    team[message['team_b_player_stats']][message['extra_data']] = message['value']
                    match.team_b_player_stats = json.dumps(team)
                    if message['extra_data'] == 'steal':
                        nu = match.team_b_steal - previous_value
                        match.team_b_steal = nu + message['value']
                    elif message['extra_data'] == 'block':
                        nu = match.team_b_block - previous_value
                        match.team_b_block = nu + message['value']
                    elif message['extra_data'] == 'assist':
                        nu = match.team_b_assist - previous_value
                        match.team_b_assist = nu + message['value']
                    match.save()
            return {'team_a_player_stats': json.loads(match.team_a_player_stats), 'team_b_player_stats': json.loads(match.team_b_player_stats),
                    'match_id': match.match_id, 'team_a_1': match.team_a_1, 'team_a_2': match.team_a_2, 'team_a_3': match.team_a_3,
                    'team_b_1': match.team_b_1, 'team_b_2': match.team_b_2, 'team_b_3': match.team_b_3}
        elif content == 'ranking':
            rank_id = data+'__'
            if message['extra_data'] == 'rebound':
                player_rank = list(PlayerRanking.objects.filter(player_rank_id__istartswith=rank_id).order_by('-rebound').values('player_name', 'rebound'))
                team_rank = list(TeamRanking.objects.filter(team_rank_id__startswith=rank_id).order_by('-rebound').values('team_name', 'rebound'))
            elif message['extra_data'] == 'points':
                player_rank = list(PlayerRanking.objects.filter(player_rank_id__istartswith=rank_id).order_by('-points').values('player_name', 'points'))
                team_rank = list(TeamRanking.objects.filter(team_rank_id__startswith=rank_id).order_by('-points').values('team_name', 'points'))
            elif message['extra_data'] == 'steal':
                player_rank = list(PlayerRanking.objects.filter(player_rank_id__istartswith=rank_id).order_by('-steal').values('player_name', 'steal'))
                team_rank = list(TeamRanking.objects.filter(team_rank_id__startswith=rank_id).order_by('-steal').values('team_name', 'steal'))
            elif message['extra_data'] == 'block':
                player_rank = list(PlayerRanking.objects.filter(player_rank_id__istartswith=rank_id).order_by('-block').values('player_name', 'block'))
                team_rank = list(TeamRanking.objects.filter(team_rank_id__startswith=rank_id).order_by('-block').values('team_name', 'block'))
            else:
                player_rank = list(PlayerRanking.objects.filter(player_rank_id__istartswith=rank_id).order_by('-assist').values('player_name', 'assist'))
                team_rank = list(TeamRanking.objects.filter(team_rank_id__startswith=rank_id).order_by('-assist').values('team_name', 'assist'))
            return {'team': team_rank, 'player': player_rank}
        elif content == 'check if youtuber or not':
            account = Account.objects.get(userName=data)
            return account.is_youtuber
        elif content == 'start homepage' or content == 'update home page':
            youtube_is_live = list(Youtube.objects.filter(is_live=True).order_by('-id').values('video_id'))
            youtube_video = list(Youtube.objects.filter(is_live=False).order_by('-id').values('video_id'))
            self.homepage = youtube_video
            live_match = list(Match.objects.filter(status='live').values('match_id', 'match_between', 'date', 'match_venue'))
            serializer = MatchSerializer(live_match, many=True)
            self.live_match = serializer.data
            youtube = Paginator(self.homepage, 5)
            match = Paginator(self.live_match, 10)
            y_next = 0
            m_next = 0
            if 'live match next page number' in message:
                m = match.get_page(message['live match next page number'])
                if m.has_next():
                    m_next = m.next_page_number()
                return {'Live Streaming': youtube_is_live, 'Live Match': m.object_list, 'live_match_next_page': m_next}
            elif 'other video next page number' in message:
                y = youtube.get_page(message['other video next page number'])
                if y.has_next():
                    y_next = y.next_page_number()
                return {'Live Streaming': youtube_is_live, 'Other Video': y.object_list, 'other_video_next_page': y_next}
            m = match.get_page(data)
            y = youtube.get_page(data)
            if y.has_next():
                y_next = y.next_page_number()
            if m.has_next():
                m_next = m.next_page_number()
            return {'Live Streaming': youtube_is_live, 'Live Match': m.object_list, 'Other Video': y.object_list,
                    'live_match_next_page': m_next, 'other_video_next_page': y_next}
        elif content == 'add youtube id':
            youtube = Youtube(is_live=message['is_live'], video_id=data)
            youtube.save()
            return 'Done'
        elif content == 'Get Tournament of Specific date':
            date = datetime.strptime(data, "%d-%m-%Y")
            tour = list(Tournament.objects.filter(tour_date=date).values('tour_name', 'tour_id', 'tour_venue'))
            return tour


async def match_started_by_ref(match_id, a_5, b_5, status, quarter, id):
    roo = 'chat_%s' % match_id
    ref_room = 'chat_%s' % match_id + '_ref'
    await channel_layer.group_send(
        roo,
        {
            'type': 'chat_message',
            'message': {"team_a_player_stats": a_5, "team_b_player_stats": b_5, "status": status, 'quarter': quarter},
            'from': 'Match Started by ref to viewer',
        }
    )
    await channel_layer.group_send(
        ref_room,
        {
            'type': 'chat_message',
            'message': {"team_a_player_stats": a_5, "ref_id": id, "team_b_player_stats": b_5, "status": status, 'quarter': quarter},
            'from': 'Match Started by ref to ref',
        }
    )


async def match_scoring(match_id, a_5, b_5, a1, a2, a3, b1, b2, b3):
    roo = 'chat_%s' % match_id
    await channel_layer.group_send(
        roo,
        {
            'type': 'chat_message',
            'message': {"team_a_player_stats": a_5, "team_b_player_stats": b_5, 'team_a_1': a1, 'team_a_2': a2, 'team_a_3': a3,
                        'team_b_1': b1, 'team_b_2': b2, 'team_b_3': b3},
            'from': 'scoring',
        }
    )
