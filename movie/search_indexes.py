import datetime
from haystack import indexes
from .models import Entry


class EntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # year = indexes.CharField(model_attr='year')
    # rate_date = indexes.DateField(model_attr='rate_date')
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Entry

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter()