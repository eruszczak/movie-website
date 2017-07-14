from django.db.models import Count
from django.views.generic import ListView, TemplateView

from .models import Title


# class GroupByYearView(ListView):
#     queryset = Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year')
#     template_name = 'groupby_year.html'
#     context_object_name = 'year_count'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title_count'] = Title.objects.all().count()
#         return context


class GroupByYearView(TemplateView):
    template_name = 'groupby_year.html'

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {
            'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
            'title_count': Title.objects.all().count()
        }
        return context
