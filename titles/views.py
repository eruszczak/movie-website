from django.contrib.auth import get_user_model
from django.db.models import Count, Subquery, Q, Avg
from django.db.models import OuterRef
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, TemplateView, RedirectView, ListView

from accounts.models import UserFollow
from lists.models import Watchlist, Favourite
from shared.mixins import LoginRequiredMixin
from shared.views import SearchViewMixin
from titles.forms import TitleSearchForm, RatingFormset
from .models import Title, Rating, Popular, CastTitle, Person, CrewTitle, NowPlaying, Upcoming, CurrentlyWatchingTV

User = get_user_model()


class HomeTemplateView(TemplateView):
    template_name = 'titles/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # this prefetches do nothing
        current_popular = Popular.objects.filter(active=True).prefetch_related('movies', 'tv', 'persons').first()
        if current_popular:
            context.update({
                'update_date': current_popular.update_date,
                'popular_movies': current_popular.movies.all().order_by('-create_date')
                    .annotate_fav_and_watch(self.request.user)
                    .annotate_rates(request_user=self.request.user),
                'popular_tv': current_popular.tv.all().annotate_rates(request_user=self.request.user),
                'popular_persons': current_popular.persons.all(),
            })

        now_playing = NowPlaying.objects.filter(active=True).prefetch_related('titles').first()
        # this prefetches do nothing ?
        if now_playing:
            context['now_playing'] = now_playing.titles.all().order_by('-release_date')\
                .annotate_rates(request_user=self.request.user)

        upcoming = Upcoming.objects.filter(active=True).prefetch_related('titles').first()
        # this prefetches do nothing ?
        if upcoming:
            context['upcoming'] = upcoming.titles.upcoming().order_by('release_date')\
                .annotate_rates(request_user=self.request.user)

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

        qs = qs.annotate_fav_and_watch(self.request.user).annotate_rates(request_user=self.request.user)

        if self.searched_user:
            # TODO: problem - any annotation makes titles distinct which I don't want in this case
            # i think i should use Rating qs? because in this case I don't want latest rating
            # anyway, it will make searching a mess.
            # maybe use Rating.values(). but it won't make a searching problem disappear
            qs = qs.annotate_rates(user=self.searched_user).order_by('-rating__rate_date')
        else:
            qs = qs.order_by('-release_date', '-name')

        return qs.prefetch_related('genres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        len_of_get = len(self.request.GET)
        only_user_ratings = self.searched_user and len_of_get == 1
        only_pagination_and_ratings = self.request.GET.get('page') and len_of_get == 2 and self.searched_user

        # hide search box if:
        # - looking for a user's ratings (or paginated ratings)
        # - there is no GET parameters
        show_search_box = (len_of_get > 1 or (len_of_get > 0 and not only_user_ratings))\
                          and not only_pagination_and_ratings

        context.update({
            'searched_user': self.searched_user,
            'show_search_box': show_search_box,
            'owner_looks_on_his_ratings': self.searched_user and self.request.user and self.request.user.pk == self.searched_user.pk
        })
        return context


class TitleDetailView(DetailView):
    query_pk_and_slug = False
    template_name = 'titles/title_detail.html'
    model = Title

    def get_queryset(self):
        queryset = super().get_queryset().filter(imdb_id=self.kwargs['imdb_id']).prefetch_related('seasons', 'keywords')\
            .annotate_fav_and_watch(self.request.user)
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                currently_watching=Subquery(
                    CurrentlyWatchingTV.objects.filter(user=self.request.user, title=OuterRef('pk')).values('pk')
                ),
            )
        return queryset

    def get_object(self, queryset=None):
        obj = self.get_queryset().get()
        if obj.should_get_details:
            obj.get_details()
        # consider if update() it if it wasn't updated for like 50 days
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        similar_titles = self.object.similar.all()
        if self.object.collection:
            context['collection_titles'] = self.object.collection.titles.annotate_rates(
                request_user=self.request.user).order_by('release_date')
            similar_titles = similar_titles.exclude(pk__in=context['collection_titles'].values_list('pk', flat=True))

        if self.request.user.is_authenticated:
            context.update({
                'user_ratings_of_title': Rating.objects.filter(user=self.request.user, title=self.object),
                'is_favourite_for_user': Favourite.objects.filter(user=self.request.user, title=self.object).exists(),
                'is_in_user_watchlist': Watchlist.objects.filter(
                    user=self.request.user, title=self.object, deleted=False).exists(),
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
            })

            summary = Rating.objects.filter(title=self.object).aggregate(avg=Avg('rate'), votes=Count('pk'))
            context.update({
                'avg': round(summary['avg'], 2) if summary['avg'] else 0,
                'votes': summary['votes']
            })

        context.update({
            'similar': similar_titles.annotate_rates(request_user=self.request.user),
            'recommendations': self.object.recommendations.annotate_rates(request_user=self.request.user),
            'cast_list': CastTitle.objects.filter(title=self.object).select_related('person')[:20],
            'crew_list': CrewTitle.objects.filter(title=self.object).select_related('person'),
        })
        return context


class RatingUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'titles/rating_update.html'
    formset_class = RatingFormset
    title = None

    def dispatch(self, request, *args, **kwargs):
        self.title = Title.objects.get(imdb_id=self.kwargs['imdb_id'])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset()
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def get_formset(self):
        if self.request.POST:
            return self.formset_class(data=self.request.POST, **self.get_formset_kwargs())
        return self.formset_class(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        return {
            'user': self.request.user,
            'title': self.title
        }

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

    def formset_valid(self, formset):
        formset.save()
        return HttpResponseRedirect(reverse('rating-update', args=[self.kwargs['imdb_id']]))

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.title
        if 'formset' not in kwargs:
            kwargs['formset'] = self.get_formset()
        return super().get_context_data(**kwargs)


class TitleRedirectView(RedirectView):
    pattern_name = 'title-detail'

    def get_redirect_url(self, *args, **kwargs):
        title = get_object_or_404(Title, imdb_id=kwargs['imdb_id'])
        return title.get_absolute_url()


class PersonDetailView(DetailView):
    model = Person
    template_name = 'titles/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        casttitle_list = CastTitle.objects.filter(
            person=self.object).select_related('title').order_by('-title__release_date')
        crewtitle_list = CrewTitle.objects.filter(
            person=self.object).select_related('title').order_by('-title__release_date')

        if self.request.user.is_authenticated:
            latest_rate = {
                'request_user_rate': Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('title')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            }
            casttitle_list = casttitle_list.annotate(**latest_rate)
            crewtitle_list = crewtitle_list.annotate(**latest_rate)

            results = list(casttitle_list.values('request_user_rate', 'title'))
            results.extend(list(crewtitle_list.values('request_user_rate', 'title')))
            rates = [result['request_user_rate'] for result in results]
            titles = [result['title'] for result in results]

            common_titles_count = Title.objects.filter(
                rating__user=self.request.user).distinct().filter(pk__in=titles).count()
            rates_clean = [r for r in rates if r]

            try:
                context['avg'] = sum(rates_clean) / len(rates_clean)
            except ZeroDivisionError:
                pass

            try:
                context['percentage'] = round((common_titles_count / len(results)) * 100, 2)
            except ZeroDivisionError:
                pass

        context.update({
            'casttitle_list': casttitle_list,
            'crewtitle_list': crewtitle_list,
            'titles_count': len(crewtitle_list) + len(casttitle_list),
            'latest_title': Title.objects.filter(
                Q(casttitle__person=self.object) | Q(crewtitle__person=self.object)).latest('release_date')
        })
        return context
