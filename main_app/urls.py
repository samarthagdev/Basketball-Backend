from django.urls import re_path
from . import views

urlpatterns = [
    re_path('players', views.creating_player, name='creating'),
    re_path('teamcreating', views.creating_team, name='teamCreating'),
    re_path('joiningteam', views.joining_team, name='joiningTeam'),
    re_path('addingplayer', views.adding_player, name='addingPlayer'),
    re_path('creatingtournament', views.creating_tournament, name='creatingTournament'),
    re_path('tourjoining', views.joining_tournament, name='tourJoining'),
    re_path('sendingjoinrequest', views.sending_request_tournament, name='sendingJoinRequest'),
    re_path('uploadingfixture', views.uploading_fixture, name='uploadingFixture'),
    re_path('addmatches', views.adding_matches, name='addMatches'),
    # re_path('changes/', views.changes, name='changes')
]
