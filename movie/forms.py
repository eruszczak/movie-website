from django import forms
from django.db.models import Q, Count

from movie.models import Title, Genre, Rating
from movie.shared import SearchFormMixin


class TitleSearchForm(SearchFormMixin, forms.Form):
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.annotate(num=Count('title')).order_by('-num'))

    @staticmethod
    def search_genre(value):
        print(value)
        return Q()


class RateUpdateForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ('rate_date', 'rate')


    # search_result = []
    # page = request.GET.get('page')
    #
    # selected_type = request.GET.get('t', '')
    # query = request.GET.get('q')
    # plot = request.GET.get('p')
    # actor = request.GET.get('a')
    # director = request.GET.get('d')
    # genres = request.GET.getlist('g')
    # username = request.GET.get('u')
    # rating = request.GET.get('r')# if validate_rate(request.GET.get('r')) else None
    # show_all_ratings = request.GET.get('all_ratings')
    # rate_date_year = request.GET.get('year')
    # rate_date_month = request.GET.get('month')
    # year = request.GET.get('y')
    # common = request.GET.get('common')
    # exclude_his = request.GET.get('exclude_his')
    # exclude_mine = request.GET.get('exclude_mine')
    #
    # if year:
    #     find_years = re.match(r'(\d{4})-*(\d{4})*', year)
    #     if find_years is not None:
    #         first_year, second_year = find_years.group(1), find_years.group(2)
    #         if first_year and second_year:
    #             if second_year < first_year:
    #                 first_year, second_year = second_year, first_year
    #             titles = titles.filter(year__lte=second_year, year__gte=first_year)
    #             search_result.append('Released between {} and {}'.format(first_year, second_year))
    #         elif first_year:
    #             titles = titles.filter(year=first_year)
    #             search_result.append('Released in {}'.format(first_year))
    #
    # if selected_type in ('movie', 'series'):
    #     titles = titles.filter(type__name=selected_type)
    #     search_result.append('Type: ' + selected_type)
    #
    # if query:
    #     titles = titles.filter(name__icontains=query) if len(query) > 2 else titles.filter(name__istartswith=query)
    #     search_result.append('Title {} "{}"'.format('contains' if len(query) > 2 else 'starts with', query))
    #
    # if plot:
    #     titles = titles.filter(plot__icontains=plot) if len(plot) > 2 else titles.filter(plot__istartswith=plot)
    #     search_result.append('Plot {} "{}"'.format('contains' if len(plot) > 2 else 'starts with', plot))
    #
    # if director:
    #     d = Director.objects.filter(id=director).first()
    #     if d is not None:
    #         titles = titles.filter(director=d)
    #         search_result.append('Directed by {}'.format(d.name))
    #
    # if actor:
    #     a = Actor.objects.filter(id=actor).first()
    #     if a is not None:
    #         titles = titles.filter(actor=a)
    #         search_result.append('With {}'.format(a.name))
    #
    # if genres:
    #     for genre in genres:
    #         titles = titles.filter(genre__name=genre)
    #     search_result.append('Genres: {}'.format(', '.join(genres)))
    #
    # want_req_user_rate = True
    #
    # req_user_id = request.user.id if request.user.is_authenticated() else 0
    # searched_user = User.objects.filter(username=username).first()
    # is_owner = request.user == searched_user
    # if searched_user:
    #     if exclude_his and req_user_id:
    #         titles = titles.filter(rating__user=request.user).exclude(rating__user=searched_user)
    #         search_result.append('Seen by you and not by {}'.format(searched_user.username))
    #     elif exclude_mine and req_user_id and req_user_id != searched_user.id:
    #         want_req_user_rate = False
    #
    #         titles = titles.filter(rating__user=searched_user).distinct().extra(select={
    #             'user_curr_rating': select_current_rating,
    #         }, select_params=[searched_user.id])
    #         titles = titles.exclude(rating__user=req_user_id)
    #         search_result.append('Seen by {} and not by me'.format(searched_user.username))
    #     elif common and req_user_id and not is_owner:
    #         titles = titles.filter(rating__user=searched_user).filter(rating__user=request.user).distinct().extra(select={
    #             'user_curr_rating': select_current_rating,
    #         }, select_params=[searched_user.id])
    #         search_result.append('Seen by you and {}'.format(searched_user.username))
    #     elif rating:
    #         titles = titles.filter(rating__user=searched_user).annotate(max_date=Max('rating__rate_date'))\
    #             .filter(rating__rate_date=F('max_date'), rating__rate=rating) \
    #             .extra(select={
    #                 'user_curr_rating': select_current_rating,
    #             }, select_params=[searched_user.id])
    #         search_result.append('Titles {} rated {}'.format(searched_user.username, rating))
    #     elif show_all_ratings:
    #         titles = Title.objects.filter(rating__user__username=searched_user.username) \
    #             .order_by('-rating__rate_date', '-rating__inserted_date')
    #         search_result.append('Seen by {}'.format(searched_user.username))
    #         search_result.append('Showing all ratings (duplicated titles)')
    #     elif not is_owner:
    #         titles = titles.filter(rating__user=searched_user).distinct().extra(select={
    #             'user_curr_rating': select_current_rating,
    #         }, select_params=[searched_user.id])
    #         search_result.append('Seen by {}'.format(searched_user.username))
    #     else:
    #         titles = titles.filter(rating__user=searched_user).order_by('-rating__rate_date')
    #         search_result.append('Seen by {}'.format(searched_user.username))
    # elif rating and req_user_id:
    #     titles = titles.filter(rating__user=request.user)\
    #         .annotate(max_date=Max('rating__rate_date'))\
    #         .filter(rating__rate_date=F('max_date'), rating__rate=rating)
    #     search_result.append('Titles you rated {}'.format(rating))
    #
    # if rate_date_year and (username or req_user_id):
    #     if rate_date_year and rate_date_month:
    #         # here must be authenticated
    #         what_user_for = searched_user or request.user
    #         titles = titles.filter(rating__user=what_user_for, rating__rate_date__year=rate_date_year,
    #                                rating__rate_date__month=rate_date_month)
    #         search_result.append('Seen in {} {}'.format(calendar.month_name[int(rate_date_month)], rate_date_year))
    #     elif rate_date_year:
    #         if username:
    #             titles = titles.filter(rating__user__username=username, rating__rate_date__year=rate_date_year)
    #         elif request.user.is_authenticated():
    #             titles = titles.filter(rating__user=request.user, rating__rate_date__year=rate_date_year)
    #         search_result.append('Seen in ' + rate_date_year)
    #
    # titles = titles.prefetch_related('director', 'genre')  # .distinct()
    # if request.user.is_authenticated() and want_req_user_rate:
    #     titles = titles.extra(select={
    #         'req_user_curr_rating': select_current_rating,
    #     }, select_params=[request.user.id])
    #
    # ratings = paginate(titles, page, 25)
    #
    # # clean get parameters, but this only works in pagination links
    # mutable_request_get = request.GET.copy()
    # mutable_request_get.pop('page', None)
    # empty_get_parameters = [k for k, v in mutable_request_get.items() if not v]
    # for key in empty_get_parameters:
    #     del mutable_request_get[key]
    # query_string = mutable_request_get.urlencode()
    #
    # context = {
    #     'page_title': 'Explore',
    #     'ratings': ratings,
    #     'searched_genres': genres,
    #     'search_result': search_result,
    #     'genres': Genre.objects.annotate(num=Count('title')).order_by('-num'),
    #     'followed_users': UserFollow.objects.filter(user_follower=request.user) if req_user_id else [],
    #     'query_string': '&{}'.format(query_string) if query_string else query_string,
    # }