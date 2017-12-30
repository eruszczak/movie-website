from django.contrib import admin

from titles.models import Keyword, Genre, Person, CastTitle, CrewTitle, Popular, NowPlaying, Upcoming, \
    CurrentlyWatchingTV, Title, Rating, Season


class RatingAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('title', 'user')


class CastTitleAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('person', 'title')


class CrewTitleAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('person', 'title')


class TVAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('title', 'user')


admin.site.register(Keyword)
admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(CastTitle, CastTitleAdmin)
admin.site.register(CrewTitle, CrewTitleAdmin)
admin.site.register(Popular)
admin.site.register(NowPlaying)
admin.site.register(Upcoming)
admin.site.register(CurrentlyWatchingTV, TVAdmin)
admin.site.register(Title)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Season)
