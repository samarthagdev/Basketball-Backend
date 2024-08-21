from django.contrib import admin
from .models import Players, Team, Tournament, Match, TeamRanking, PlayerRanking, Youtube
# Register your models here.


class MainAppAdmin(admin.ModelAdmin):
    list_display = ('userName', 'address')
    search_fields = ('userName', 'address')


class MainAppAdmin1(admin.ModelAdmin):
    list_display = ('team_name', 'owner')
    search_fields = ('team_name', 'owner')


class MainAppAdmin2(admin.ModelAdmin):
    list_display = ('tour_name', 'tour_owner')
    search_fields = ('tour_name', 'tour_owner')


class MainAppAdmin3(admin.ModelAdmin):
    list_display = ('tour_id',)
    search_fields = ('tour_id',)


class MainAppAdmin4(admin.ModelAdmin):
    list_display = ('team_rank_id', 'team_name')
    search_fields = ('team_rank_id', 'team_name')


class MainAppAdmin5(admin.ModelAdmin):
    list_display = ('player_rank_id', 'player_name')
    search_fields = ('player_rank_id', ' player_name')


class MainAppAdmin6(admin.ModelAdmin):
    list_display = ('video_id', 'is_live')
    search_fields = ('video_id', ' is_live')


admin.site.register(Players, MainAppAdmin)
admin.site.register(Team, MainAppAdmin1)
admin.site.register(Tournament, MainAppAdmin2)
admin.site.register(Match, MainAppAdmin3)
admin.site.register(TeamRanking, MainAppAdmin4)
admin.site.register(PlayerRanking, MainAppAdmin5)
admin.site.register(Youtube, MainAppAdmin6)

