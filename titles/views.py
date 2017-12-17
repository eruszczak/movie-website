from django.contrib.auth import get_user_model
from django.db.models import Count, When, Case, IntegerField, Subquery, Q, Avg
from django.db.models import OuterRef
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView, RedirectView, ListView, UpdateView

from accounts.models import UserFollow
from lists.models import Watchlist, Favourite
from shared.views import SearchViewMixin
from titles.constants import TITLE_TYPE_CHOICES
from titles.forms import TitleSearchForm, RateUpdateForm
from .models import Title, Rating, Popular, CastTitle, Person, CrewTitle, NowPlaying, Upcoming


User = get_user_model()


class HomeTemplateView(TemplateView):
    template_name = 'titles/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_popular = Popular.objects.filter(active=True).prefetch_related('movies', 'tv', 'persons').first()
        if current_popular:
            context.update({
                'update_date': current_popular.update_date,
                'popular_movies': current_popular.movies.all(),
                'popular_tv': current_popular.tv.all(),
                'popular_persons': current_popular.persons.all(),
            })

        now_playing = NowPlaying.objects.filter(active=True).prefetch_related('titles').first()
        if now_playing:
            context['now_playing'] = now_playing.titles.all().order_by('-release_date')

        upcoming = Upcoming.objects.filter(active=True).prefetch_related('titles').first()
        if upcoming:
            context['upcoming'] = upcoming.titles.upcoming().order_by('release_date')

        if self.request.user.is_authenticated:
            request_user_ratings = Rating.objects.filter(
                user=self.request.user, title=OuterRef('pk')
            ).order_by('-rate_date').values('rate')

            if context.get('popular_movies'):
                context['popular_movies'] = context['popular_movies'].annotate(
                    has_in_watchlist=Count(
                        Case(
                            When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                            output_field=IntegerField()
                        )
                    ),
                    has_in_favourites=Count(
                        Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                    ),
                    request_user_rate=Subquery(request_user_ratings[:1])
                )

            for key in ['popular_tv', 'now_playing', 'upcoming']:
                if context.get(key):
                    context[key] = context[key].annotate(request_user_rate=Subquery(request_user_ratings[:1]))

        return context


class TitleListView(SearchViewMixin, ListView):
    search_form_class = TitleSearchForm
    template_name = 'titles/title_list.html'
    paginate_by = 20
    model = Title
    searched_user = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get('user'):
            self.searched_user = self.search_form.cleaned_data.get('user')

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                has_in_watchlist=Count(
                    Case(
                        When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                        output_field=IntegerField()
                    )
                ),
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                ),
                request_user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('pk')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )

        if self.searched_user:
            # TODO: problem - any annotation makes titles distinct which I don't want in this case
            # i think i should use Rating qs? because in this case I don't want latest rating
            # anyway, it will make searching a mess.
            # maybe use Rating.values(). but it won't make a searching problem disappear
            qs = qs.annotate(
                searched_user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.searched_user, title=OuterRef('pk')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            ).order_by('-rating__rate_date')
        else:
            qs = qs.order_by('-release_date', '-name')

        return qs.prefetch_related('genres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'searched_user': self.searched_user,
            'type_choices': self.get_title_type_choices()
        })
        return context

    @staticmethod
    def get_title_type_choices():
        type_choices = [('', 'Both')]
        type_choices.extend([(str(value), display) for value, display in TITLE_TYPE_CHOICES])
        return type_choices


class TitleDetailView(DetailView):
    query_pk_and_slug = False
    template_name = 'titles/title_detail.html'
    model = Title
    object = None

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                ),
                has_in_watchlist=Count(
                    Case(
                        When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                        output_field=IntegerField()
                    )
                ),
            )

        try:
            obj = queryset.get(imdb_id=self.kwargs['imdb_id'])
        except self.model.DoesNotExist:
            raise Http404
        else:
            obj.call_update_task()
            return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection_titles = Title.objects.none()
        similar_titles = self.object.similar.all()
        if self.object.collection:
            collection_titles = self.object.collection.titles.all()
            similar_titles = similar_titles.exclude(pk__in=collection_titles.values_list('pk', flat=True))

        recommendations = self.object.recommendations.all()

        if self.request.user.is_authenticated:
            context.update({
                # 'rating': Rating.objects.filter(user=self.request.user, title=self.object).latest('rate_date'),
                'user_ratings_of_title': Rating.objects.filter(user=self.request.user, title=self.object),
                'is_favourite_for_user': Favourite.objects.filter(user=self.request.user, title=self.object).exists(),
                'is_in_user_watchlist': Watchlist.objects.filter(
                    user=self.request.user, title=self.object, deleted=False).exists(),
                'followed_title_not_recommended': UserFollow.objects.filter(follower=self.request.user).exclude(
                    Q(followed__rating__title=self.object) | Q(followed__recommendation__title=self.object)
                ).select_related('followed'),
                # 'recommend_form': self.recommend_form_class(self.request.user, self.object),
                'followed_saw_title': UserFollow.objects.filter(
                    follower=self.request.user, followed__rating__title=self.object).annotate(
                    user_rate=Subquery(
                        Rating.objects.filter(
                            user=OuterRef('followed'), title=OuterRef('followed__rating__title')
                        ).order_by('-rate_date').values('rate')[:1]
                    ),
                    user_rate_date=Subquery(
                        Rating.objects.filter(
                            user=OuterRef('followed'), title=OuterRef('followed__rating__title')
                        ).order_by('-rate_date').values('rate_date')[:1]
                    )
                ).select_related('followed'),
                'summary': Rating.objects.filter(title=self.object).aggregate(avg=Avg('rate'), votes=Count('pk'))
            })

            request_user_newest_ratings = Rating.objects.filter(
                user=self.request.user, title=OuterRef('pk')
            ).order_by('-rate_date').values('rate')[:1]

            collection_titles = collection_titles.annotate(request_user_rate=Subquery(request_user_newest_ratings))
            similar_titles = similar_titles.annotate(request_user_rate=Subquery(request_user_newest_ratings))
            recommendations = recommendations.annotate(request_user_rate=Subquery(request_user_newest_ratings))

        context.update({
            'similar': similar_titles,
            'recommendations': recommendations,
            'collection_titles': collection_titles,
            'cast_list': CastTitle.objects.filter(title=self.object).select_related('person'),
            'crew_list': CrewTitle.objects.filter(title=self.object).select_related('person'),
        })
        return context

    # @method_decorator(login_required)
    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     # self.delete_rating()
    #     return redirect(self.object)

    # def delete_rating(self):
    #     delete_rating = self.request.POST.get('delete_rating')
    #     rating_pk = self.request.POST.get('rating_pk')
    #     if delete_rating and rating_pk:
    #         to_delete = Rating.objects.filter(pk=rating_pk, user=self.request.user).first()
    #         query = {
    #                 'user': self.request.user,
    #                 'title': self.object,
    #                 'added_date__date__lte': to_delete.rate_date,
    #                 'deleted': True
    #         }
    #         in_watchlist = Watchlist.objects.filter(**query).first()
    #         if in_watchlist:
    #             toggle_title_in_watchlist(watch=True, instance=in_watchlist)
    #         to_delete.delete()


class RatingUpdateView(UpdateView):
    model = Rating
    template_name = 'titles/rating_update.html'
    form_class = RateUpdateForm


# class GroupByGenreView(TemplateView):
#     template_name = 'titles/group_by_genre.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context.update({
#             'genre': Genre.objects.annotate(num=Count('title')).order_by('-num')
#         })
#         return context
#
#
# class GroupByDirectorView(TemplateView):
#     template_name = 'titles/group_by_director.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # context.update({
#         #     'director': Director.objects.filter(
#         #         title__type__name='title').annotate(num=Count('title')).order_by('-num')[:50]
#         # })
#         return context
#
#
# class GroupByYearView(TemplateView):
#     template_name = 'titles/group_by_year.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context.update({
#             'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
#             'title_count': Title.objects.all().count()
#         })
#         return context


class TitleRedirectView(RedirectView):
    pattern_name = 'title-detail'

    def get_redirect_url(self, *args, **kwargs):
        title = get_object_or_404(Title, imdb_id=kwargs['imdb_id'])
        return title.get_absolute_url()


class PersonDetailView(DetailView):
    model = Person
    template_name = 'titles/person_detail.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('casttitle_set__title', 'crewtitle_set__title')
