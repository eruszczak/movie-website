from django.contrib import admin

from lists.models import Favourite, Watchlist


admin.site.register(Favourite)
admin.site.register(Watchlist)