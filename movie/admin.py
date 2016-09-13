from django.contrib import admin
from .models import Entry


class EntryModelADmin(admin.ModelAdmin):
    fields = 'const rate rate_imdb rate_date runtime year release_date votes img watch_again_date'.split()

    class Meta:
        model = Entry

admin.site.register(Entry, EntryModelADmin)