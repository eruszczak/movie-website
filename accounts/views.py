from os.path import join

from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Subquery, F, Avg, Exists
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, UpdateView, DetailView, FormView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from accounts.helpers import import_ratings_from_csv
from shared.mixins import LoginRequiredMixin
from titles.constants import SERIES, MOVIE
from titles.helpers import SubqueryCount
from titles.models import Title, Rating
from accounts.models import UserFollow
from accounts.forms import UserUpdateForm, ImportRatingsForm


User = get_user_model()


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_edit.html'

    def get_object(self, queryset=None):
        return super().get_queryset().get(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, 'Settings updated.')
        return self.get_object().edit_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['original_instance'] = self.request.user
        return kwargs


class UserListView(ListView):
    template_name = 'accounts/user_list.html'
    paginate_by = 20
    searched_title = None
    model = User

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('imdb_id'):
            self.searched_title = get_object_or_404(Title, imdb_id=self.request.GET['imdb_id'])
            queryset = queryset.filter(rating__title=self.searched_title).annotate(
                user_rate=Subquery(
                    Rating.objects.filter(
                        user=OuterRef('pk'), title=OuterRef('rating__title')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            ).distinct()

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                already_follows=Exists(UserFollow.objects.filter(follower=self.request.user, followed=OuterRef('pk')))
            )
        return queryset.annotate(
            # todo
            titles_count=Count('rating')
        ).order_by('-titles_count')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.searched_title:
            context.update({
                'title': self.searched_title,
            })
        return context


class UserDetailView(DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    limit = 15

    def get_queryset(self):
        queryset = super().get_queryset().filter(username=self.kwargs['username']).annotate(
            total_movies=SubqueryCount(
                Rating.objects.filter(title__type=MOVIE, user=OuterRef('pk')).order_by().distinct('title')
            ),
            total_series=SubqueryCount(
                Rating.objects.filter(title__type=SERIES, user=OuterRef('pk')).order_by().distinct('title')
            ),
            total_followers=SubqueryCount(
                UserFollow.objects.filter(followed=OuterRef('pk'))
            ),
            total_ratings=Count('rating'),
        )

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                already_follows=Exists(UserFollow.objects.filter(follower=self.request.user, followed=OuterRef('pk')))
            )
        return queryset

    def get_object(self, queryset=None):
        return self.get_queryset().get()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_owner = self.object.pk == self.request.user.pk
        is_other_user = self.request.user.is_authenticated and not is_owner

        ratings = Rating.objects.filter(user=self.object).select_related('title')
        currently_watching = Title.objects.filter(currentlywatchingtv__user=self.object).annotate(
            user_rate=Subquery(
                Rating.objects.filter(user=self.object, title=OuterRef('pk')).order_by('-rate_date').values('rate')[:1]
            )
        )

        if self.request.user.is_authenticated:
            ratings = ratings.annotate(
                request_user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('title')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )
            currently_watching = currently_watching.annotate(
                request_user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('pk')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )

        if is_other_user:
            context.update({
                'already_follows': UserFollow.objects.filter(follower=self.request.user, followed=self.object).exists(),
                'comparision': self.get_ratings_comparision()
            })
        elif is_owner:
            context['form'] = ImportRatingsForm()

        context.update({
            'is_other_user': is_other_user,
            'is_owner': is_owner,
            'rating_list': ratings[:self.limit],
            'currently_watching': currently_watching[:self.limit],
            'feed': Rating.objects.filter(
                user__in=UserFollow.objects.filter(follower=self.object).values_list('followed', flat=True)
            ).select_related('title', 'user').order_by('-rate_date')[:self.limit]
        })
        return context

    def get_ratings_comparision(self):
        """
        gets additional context for a user who visits somebody else's profile
        """
        common_titles = Title.objects.filter(
            rating__user=self.object).filter(rating__user=self.request.user).distinct().annotate(
            user_rate=Subquery(
                Rating.objects.filter(
                    user=self.object, title=OuterRef('pk')
                ).order_by('-rate_date').values('rate')[:1]
            ),
            request_user_rate=Subquery(
                Rating.objects.filter(
                    user=self.request.user, title=OuterRef('pk')
                ).order_by('-rate_date').values('rate')[:1]
            )
        )

        common_titles_length = common_titles.count()
        if common_titles_length:
            titles_user_rate_higher = common_titles.filter(user_rate__gt=F('request_user_rate'))
            titles_user_rate_lower = common_titles.filter(user_rate__lt=F('request_user_rate'))
            titles_rated_the_same = common_titles.filter(user_rate=F('request_user_rate'))
            titles_user_liked = Title.objects.filter(rating__user=self.object, rating__rate__gte=7).exclude(
                rating__user=self.request.user).distinct().annotate(
                user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.object, title=OuterRef('pk')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )

            distinct_titles_count = self.object.total_movies + self.object.total_series
            return {
                'common_titles_length': common_titles_length,
                'averages': common_titles.aggregate(user=Avg('user_rate'), request_user=Avg('request_user_rate')),
                'percentage': round((common_titles_length / distinct_titles_count) * 100, 2),

                'titles_user_rate_higher': titles_user_rate_higher[:self.limit],
                'titles_user_rate_lower': titles_user_rate_lower[:self.limit],
                'titles_rated_the_same': titles_rated_the_same[:self.limit],
                'titles_user_liked': titles_user_liked[:self.limit]
            }


class ImportRatingsAPIView(LoginRequiredMixin, FormView):
    form_class = ImportRatingsForm

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def form_invalid(self, form):
        message = 'There was an error with import'
        if form['csv_file'].errors:
            message = f"Error with uploaded file for import: {form['csv_file'].errors.as_text().lstrip('* ')}"

        messages.error(self.request, message)
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        user_tmp_folder = self.request.user.get_temp_folder_path(absolute=True, create=True)
        file = form.cleaned_data['csv_file']
        file_path = join(user_tmp_folder, file.name)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        path = default_storage.save(file_path, ContentFile(file.read()))
        print('importing', path)
        import_ratings_from_csv(self.request.user, path)
        messages.success(self.request, 'You will be notified, when import is done.')
        return super().form_valid(form)
