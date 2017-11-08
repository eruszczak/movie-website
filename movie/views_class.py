from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, RedirectView, DetailView, FormView, View
from django.views.generic.edit import UpdateView

from common.prepareDB import update_title
from common.sql_queries import curr_title_rating_of_followed
from movie.functions import toggle_title_in_watchlist, create_or_update_rating, recommend_title
from users.models import UserFollow
from .models import Title, Rating, Watchlist, Favourite
from django.utils.decorators import method_decorator





class TitleDetailView(DetailView):
    template_name = 'title_details.html'
    context_object_name = 'title'
    model = Title

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        slug_or_const = self.kwargs.get('slug')
        title = Title.objects.filter(slug=slug_or_const).first()
        return title

    def get_context_data(self, **kwargs):
        req_user_data = {}
        if self.request.user.is_authenticated:
            req_user_data = {
                'user_ratings_of_title': Rating.objects.filter(user=self.request.user, title=self.object),
                'is_favourite_for_user': Favourite.objects.filter(user=self.request.user, title=self.object).exists(),
                'is_in_user_watchlist': Watchlist.objects
                    .filter(user=self.request.user, title=self.object, deleted=False)
                    .exists(),
                'followed_title_not_recommended': UserFollow.objects
                    .filter(user_follower=self.request.user)
                    .exclude(user_followed__rating__title=self.object)
                    .exclude(user_followed__recommendation__title=self.object),
                'followed_saw_title': curr_title_rating_of_followed(self.request.user.id, self.object.id)
            }

        actors_and_other_titles = []
        for actor in self.object.actor.all():
            if self.request.user.is_authenticated:
                titles = Title.objects.filter(actor=actor).exclude(const=self.object.const).extra(select={
                    'user_rate': """SELECT rate FROM movie_rating as rating
                    WHERE rating.title_id = movie_title.id
                    AND rating.user_id = %s
                    ORDER BY rating.rate_date DESC LIMIT 1"""
                }, select_params=[self.request.user.id]).order_by('-votes')[:6]
            else:
                titles = Title.objects.filter(actor=actor).exclude(const=self.object.const).order_by('-votes')[:6]

            if titles:
                actors_and_other_titles.append((actor, titles))

        context = super().get_context_data(**kwargs)
        context.update({
            'data': req_user_data,
            'actors_and_other_titles': sorted(actors_and_other_titles, key=lambda x: len(x[1]))
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.update_title()
        self.recommend_title_to_other_users()
        self.create_or_update_rating()
        self.delete_title()
        # todo: use if (allow only one action per one post) and call messages only once

        return redirect(self.object)

    def update_title(self):
        if self.request.POST.get('update_title'):
            is_updated, message = update_title(self.object)
            if is_updated:
                messages.success(self.request, message)
            else:
                messages.warning(self.request, message)

    def recommend_title_to_other_users(self):
        selected_users = self.request.POST.getlist('choose_followed_user')
        if selected_users:
            message = recommend_title(self.object, self.request.user, selected_users)
            if message:
                messages.info(self.request, message, extra_tags='safe')

    def create_or_update_rating(self):
        new_rating, insert_as_new = self.request.POST.get('rating'), self.request.POST.get('insert_as_new')
        if new_rating:
            create_or_update_rating(self.object, self.request.user, new_rating, insert_as_new)

    def delete_title(self):
        delete_rating = self.request.POST.get('delete_rating')
        rating_pk = self.request.POST.get('rating_pk')
        if delete_rating and rating_pk:
            to_delete = Rating.objects.filter(pk=rating_pk, user=self.request.user).first()
            query = {
                    'user': self.request.user,
                    'title': self.object,
                    'added_date__date__lte': to_delete.rate_date,
                    'deleted': True
            }
            in_watchlist = Watchlist.objects.filter(**query).first()
            if in_watchlist:
                toggle_title_in_watchlist(watch=True, instance=in_watchlist)
            to_delete.delete()





@method_decorator(login_required, name='dispatch')
class TitleEditView(UpdateView):
    pass